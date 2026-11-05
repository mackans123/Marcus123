import csv
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lead_filter as lf  # noqa: E402


class ClassifyRoleTest(unittest.TestCase):
    def assertBucket(self, title, bucket, company=""):
        got, why = lf.classify_role(title, company)
        self.assertEqual(got, bucket, f"{title!r} @ {company!r} -> {got} ({why})")

    def test_physical_therapists_kept(self):
        for t in ["Physical Therapist", "Senior Physical Therapist", "PT, DPT",
                  "Dr. Jane Doe, DPT", "Doctor of Physical Therapy",
                  "Physiotherapist", "Leg. fysioterapeut", "Sjukgymnast",
                  "PT Owner", "Orthopedic Physical Therapist", "P.T.", "PTA",
                  "Director of Physical Therapy"]:
            self.assertBucket(t, "pt")

    def test_physicians_excluded(self):
        for t in ["Physician", "Orthopedic Surgeon", "MD", "John Smith, M.D.",
                  "Physiatrist", "Physical Medicine & Rehabilitation", "PM&R",
                  "Läkare", "Ortoped", "DO", "Medical Doctor", "Specialistläkare"]:
            self.assertBucket(t, "physician")

    def test_physical_is_not_physician(self):
        # The classic mistake: "phys*" matching both professions.
        self.assertBucket("Physical Therapist", "pt")
        self.assertBucket("Physician", "physician")

    def test_other_professions_excluded(self):
        for t in ["Chiropractor", "Physician Assistant", "PA-C",
                  "Occupational Therapist", "Naprapat", "Registered Nurse"]:
            self.assertBucket(t, "other")

    def test_mixed_titles_go_to_review(self):
        self.assertBucket("MD, PT", "review")

    def test_support_roles_at_pt_go_to_review(self):
        for t in ["PT Aide", "Physical Therapy Receptionist", "PT Billing Specialist",
                  "Student Physical Therapist"]:
            self.assertBucket(t, "review")

    def test_leaders_depend_on_company(self):
        self.assertBucket("Owner", "pt", company="Harbor Physical Therapy")
        self.assertBucket("Clinic Director", "pt", company="Bay PT & Sports")
        self.assertBucket("Verksamhetschef", "pt", company="Fysiokliniken AB")
        self.assertBucket("Owner", "review", company="Smith Orthopedic Surgery Associates PT")
        self.assertBucket("Owner", "review", company="Acme Corp")
        self.assertBucket("CEO", "review", company="Sunrise Rehab Center")

    def test_lowercase_pt_and_do_do_not_trigger(self):
        self.assertBucket("Office manager, part-time", "review")
        self.assertBucket("What we do", "review")


class MailHostTest(unittest.TestCase):
    def test_classify(self):
        self.assertEqual(lf.classify_mail_host(["aspmx.l.google.com", "alt1.aspmx.l.google.com"]), "google")
        self.assertEqual(lf.classify_mail_host(["acme-com.mail.protection.outlook.com"]), "microsoft")
        self.assertEqual(lf.classify_mail_host(["mx1.pphosted.com"]), "other")
        self.assertEqual(lf.classify_mail_host([]), "no-mx")
        self.assertEqual(lf.classify_mail_host(None), "unknown")


def write(path: Path, rows: list[dict]) -> Path:
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return path


def read(path: Path) -> list[dict]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


class EndToEndTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def base(self, email, title, **kw):
        row = {"Email": email, "First Name": "A", "Last Name": "B", "Title": title,
               "Company Name": kw.pop("company", "Harbor Physical Therapy"),
               "status": kw.pop("status", "COMPLETED"), "category": kw.pop("category", ""),
               "reply_count": kw.pop("reply_count", "0"),
               "is_unsubscribed": kw.pop("is_unsubscribed", "false"),
               "last_email_sequence_sent": kw.pop("sent", "3")}
        row.update(kw)
        return row

    def test_reengage_flow(self):
        camp1 = write(self.tmp / "camp1.csv", [
            self.base("pt1@harbor.com", "Physical Therapist"),
            self.base("doc@ortho.com", "Orthopedic Surgeon"),
            self.base("replied@x.com", "Physical Therapist", reply_count="1"),
            self.base("unsub@x.com", "PT, DPT", is_unsubscribed="true"),
            self.base("bounce@x.com", "Physical Therapist", status="BLOCKED"),
            self.base("dnc@x.com", "Physical Therapist", category="Do Not Contact"),
            self.base("ooo@x.com", "Physical Therapist", category="Out Of Office", reply_count="1"),
            self.base("fresh@x.com", "Physical Therapist", status="NOT_STARTED", sent="0"),
            self.base("owner@acme.com", "Owner", company="Acme Corp"),
            self.base("customer@client.com", "Physical Therapist"),
        ])
        # Same person in a second campaign where they replied: excluded everywhere.
        camp2 = write(self.tmp / "camp2.csv", [
            self.base("PT1@harbor.com", "Physical Therapist", reply_count="2"),
            self.base("pt2@harbor.com", "Physical Therapist"),
        ])
        exclude = self.tmp / "customers.txt"
        exclude.write_text("client.com\n")

        out = self.tmp / "out"
        stats = lf.process([camp1, camp2], [], [exclude], out, use_mx=False, mx_cache=None)

        reengage = {r["email"] for r in read(out / "reengage.csv")}
        never = {r["email"] for r in read(out / "never_contacted.csv")}
        review = {r["email"] for r in read(out / "review.csv")}
        excluded = {r["email"]: r["role_reason"] for r in read(out / "excluded.csv")}

        self.assertEqual(reengage, {"pt2@harbor.com", "ooo@x.com"})
        self.assertEqual(never, {"fresh@x.com"})
        self.assertEqual(review, {"owner@acme.com"})
        self.assertIn("pt1@harbor.com", excluded)
        self.assertTrue(excluded["pt1@harbor.com"].startswith("replied"))
        self.assertTrue(excluded["unsub@x.com"].startswith("unsubscribed"))
        self.assertTrue(excluded["bounce@x.com"].startswith("bounced"))
        self.assertTrue(excluded["dnc@x.com"].startswith("category: do not contact"))
        self.assertTrue(excluded["customer@client.com"].startswith("on exclude list"))
        self.assertIn("physician", excluded["doc@ortho.com"])
        self.assertEqual(stats["reengage"], 2)
        self.assertTrue((out / "summary.txt").exists())

    def test_fresh_flow_with_history_and_custom_fields(self):
        history = write(self.tmp / "old.csv", [
            self.base("seen@x.com", "Physical Therapist"),
            self.base("bounced@x.com", "Physical Therapist", status="BOUNCED"),
        ])
        # Apollo-style fresh export: different headers, semicolons, no status.
        fresh = self.tmp / "apollo.csv"
        fresh.write_text(
            "First Name;Last Name;Job Title;Company;Email;Email Status\n"
            "C;D;Physical Therapist;Bay PT;new@bay.com;Verified\n"
            "E;F;Physical Therapist;Bay PT;seen@x.com;Verified\n"
            "G;H;Physical Therapist;Bay PT;bounced@x.com;Verified\n"
            "I;J;Physical Therapist;Bay PT;bad@bay.com;Invalid\n"
            "K;L;Physician;Bay Clinic;md@bay.com;Verified\n"
        )
        # Smartlead-style export with the title hidden in custom_fields JSON.
        smart = write(self.tmp / "smart.csv", [{
            "email": "cf@x.com", "first_name": "M", "last_name": "N",
            "company_name": "Some Clinic",
            "custom_fields": '{"Job Title": "Physiotherapist"}',
        }])
        out = self.tmp / "out"
        lf.process([fresh, smart], [history], [], out, use_mx=False, mx_cache=None)

        never = {r["email"] for r in read(out / "never_contacted.csv")}
        reengage = {r["email"] for r in read(out / "reengage.csv")}
        excluded = {r["email"] for r in read(out / "excluded.csv")}
        self.assertEqual(never, {"new@bay.com", "cf@x.com"})
        self.assertEqual(reengage, {"seen@x.com"})  # contacted before -> re-engage track
        self.assertEqual(excluded, {"bounced@x.com", "bad@bay.com", "md@bay.com"})

    def test_titles_filled_from_history_source_list(self):
        # Smartlead export without titles; the original Apollo list has them.
        export = write(self.tmp / "export.csv", [
            {"email": "amy@bay.com", "status": "COMPLETED", "company_name": "Bay Clinic",
             "reply_count": "0", "last_email_sequence_sent": "3"},
            {"email": "doc@bay.com", "status": "COMPLETED", "company_name": "Bay Clinic",
             "reply_count": "0", "last_email_sequence_sent": "3"},
        ])
        source = write(self.tmp / "apollo.csv", [
            {"Email": "amy@bay.com", "Title": "Physical Therapist"},
            {"Email": "doc@bay.com", "Title": "Physician"},
        ])
        out = self.tmp / "out"
        lf.process([export], [source], [], out, use_mx=False, mx_cache=None)
        self.assertEqual([r["email"] for r in read(out / "reengage.csv")], ["amy@bay.com"])
        self.assertEqual([r["email"] for r in read(out / "excluded.csv")], ["doc@bay.com"])

    def test_mx_split(self):
        camp = write(self.tmp / "c.csv", [
            self.base("a@googleco.com", "Physical Therapist"),
            self.base("b@msco.com", "Physical Therapist"),
            self.base("c@gatewayco.com", "Physical Therapist"),
        ])
        fake = {"googleco.com": ["aspmx.l.google.com"],
                "msco.com": ["msco-com.mail.protection.outlook.com"],
                "gatewayco.com": ["mx1.pphosted.com"]}
        original = lf.mx_hosts
        lf.mx_hosts = lambda d, timeout=8.0: fake[d]
        try:
            out = self.tmp / "out"
            lf.process([camp], [], [], out, use_mx=True, mx_cache=self.tmp / "cache.json")
        finally:
            lf.mx_hosts = original
        ms = {r["email"] for r in read(out / "reengage_microsoft.csv")}
        google = {r["email"] for r in read(out / "reengage_google_and_other.csv")}
        self.assertEqual(ms, {"b@msco.com"})
        self.assertEqual(google, {"a@googleco.com", "c@gatewayco.com"})
        self.assertTrue((self.tmp / "cache.json").exists())


if __name__ == "__main__":
    unittest.main()
