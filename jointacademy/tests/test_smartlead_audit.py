import contextlib
import csv
import datetime as dt
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import smartlead_audit as sa  # noqa: E402

TODAY = dt.date(2026, 11, 5)


def acc(id, email, rep="99%", status="ACTIVE", typ="GMAIL", started="2026-09-01T10:00:00Z",
        smtp=True, imap=True, **extra):
    a = {"id": id, "from_email": email, "from_name": "Leif", "type": typ,
         "is_smtp_success": smtp, "is_imap_success": imap, "message_per_day": 25,
         "daily_sent_count": 3, "client_id": None, "tags": [],
         "warmup_details": {"status": status, "warmup_reputation": rep,
                            "total_sent_count": 300, "total_spam_count": 2,
                            "warmup_created_at": started}}
    a.update(extra)
    return a


class VerdictTest(unittest.TestCase):
    def v(self, a):
        return sa.verdict(a, TODAY)[0]

    def test_ready(self):
        self.assertEqual(self.v(acc(1, "a@x.com", rep="98%")), "READY")
        self.assertEqual(self.v(acc(1, "a@x.com", rep=100)), "READY")  # numeric form

    def test_rest(self):
        self.assertEqual(self.v(acc(1, "a@x.com", rep="92%")), "REST")
        self.assertEqual(self.v(acc(1, "a@x.com", started="2026-10-30")), "REST")  # 6 days
        self.assertEqual(self.v(acc(1, "a@x.com", status="INACTIVE")), "REST")
        self.assertEqual(self.v(acc(1, "a@x.com", rep=None)), "REST")

    def test_retire(self):
        self.assertEqual(self.v(acc(1, "a@x.com", rep="80%")), "RETIRE")
        self.assertEqual(self.v(acc(1, "a@x.com", is_suspended=True)), "RETIRE")
        # Low reputation retires even when warmup was switched off.
        self.assertEqual(self.v(acc(1, "a@x.com", rep="70%", status="INACTIVE")), "RETIRE")

    def test_fix(self):
        self.assertEqual(self.v(acc(1, "a@x.com", smtp=False, smtp_failure_error="auth failed")), "FIX")
        self.assertEqual(self.v(acc(1, "a@x.com", imap=False)), "FIX")
        a = acc(1, "a@x.com")
        a["warmup_details"]["blocked_reason"] = "too many bounces"
        self.assertEqual(self.v(a), "FIX")

    def test_missing_warmup_details(self):
        a = acc(1, "a@x.com")
        a["warmup_details"] = None
        self.assertEqual(self.v(a), "REST")

    def test_unknown_start_date_does_not_block_ready(self):
        self.assertEqual(self.v(acc(1, "a@x.com", started=None)), "READY")


class HelpersTest(unittest.TestCase):
    def test_to_pct(self):
        self.assertEqual(sa.to_pct("98%"), 98.0)
        self.assertEqual(sa.to_pct(95), 95.0)
        self.assertEqual(sa.to_pct(" 97 % "), 97.0)
        self.assertIsNone(sa.to_pct(None))
        self.assertIsNone(sa.to_pct("n/a"))

    def test_provider(self):
        self.assertEqual(sa.provider_of({"type": "GMAIL"}), "Google")
        self.assertEqual(sa.provider_of({"type": "OUTLOOK"}), "Microsoft")
        self.assertEqual(sa.provider_of({"type": "SMTP", "smtp_host": "smtp.office365.com"}), "Microsoft")
        self.assertEqual(sa.provider_of({"type": "SMTP", "smtp_host": "smtp.gmail.com"}), "Google")
        self.assertEqual(sa.provider_of({"type": "ZOHO"}), "SMTP (zoho)")

    def test_as_list(self):
        self.assertEqual(sa.as_list([1]), [1])
        self.assertEqual(sa.as_list({"ok": True, "data": [2]}), [2])
        self.assertEqual(sa.as_list(None), [])


class FakeSmartlead(sa.Smartlead):
    """Serves canned responses in the shapes the Smartlead docs show.

    Subclasses the real client so its pagination logic is exercised."""

    accounts = [
        acc(1, "leif@ja-team.com", rep="99%"),                         # READY, in camp 10
        acc(2, "anna@ja-team.com", rep="88%"),                         # REST, in camp 10
        acc(3, "old@ja-mail.com", rep="60%", typ="OUTLOOK"),           # RETIRE, in camp 11
        acc(4, "ms@ja-mail.com", rep=100, typ="OUTLOOK", smtp=False),  # FIX
        acc(5, "other@otherbrand.com", rep="99%"),                     # not JA: excluded
        acc(6, "spare@ja-team.com", rep="99%", tags=[{"tag_id": 1, "tag_name": "JA-Google"}]),
    ]
    campaigns = [
        {"id": 10, "name": "JA / PT re-engage / Google / EN", "status": "ACTIVE", "client_id": None,
         "created_at": "2026-10-01T00:00:00Z", "send_as_plain_text": True},
        {"id": 11, "name": "Joint Academy - PT old", "status": "PAUSED", "client_id": None,
         "created_at": "2026-06-01T00:00:00Z"},
        {"id": 12, "name": "Otherbrand outreach", "status": "ACTIVE", "client_id": None},
    ]

    def __init__(self, api_key):
        super().__init__(api_key)
        self.calls = []

    def get(self, path, raw=False, **params):
        self.calls.append(path)
        if path == "/campaigns/":
            return self.campaigns
        if path == "/campaigns/10/email-accounts":
            return [{"id": 1, "type": "GMAIL"}, {"id": 2, "type": "GMAIL"}]
        if path == "/campaigns/11/email-accounts":
            return {"ok": True, "data": [{"id": 3, "type": "OUTLOOK"}]}
        if path == "/campaigns/10/analytics":
            return {"status": "ACTIVE", "sent_count": "900", "unique_sent_count": "400",
                    "reply_count": "8", "bounce_count": "6", "unsubscribed_count": "1",
                    "campaign_lead_stats": {"total": 600, "notStarted": 150, "inprogress": 50,
                                            "completed": 400, "blocked": 0}}
        if path == "/campaigns/11/analytics":
            return {"status": "PAUSED", "sent_count": "700", "unique_sent_count": "600",
                    "reply_count": "3", "bounce_count": "30", "unsubscribed_count": "4",
                    "campaign_lead_stats": {"total": 800, "notStarted": 100, "inprogress": 100,
                                            "completed": 600, "blocked": 0}}
        if path == "/email-accounts/":
            off = params["offset"]
            return self.accounts[off:off + 4]  # pretend the server caps pages at 4
        if path.endswith("/leads-export"):
            return ("id,status,category,first_name,email,custom_fields,reply_count\n"
                    '1,COMPLETED,,A,a@x.com,"{""Title"": ""PT""}",0\n'
                    "2,COMPLETED,,B,b@x.com,{},0\n")
        if path.endswith("/statistics"):
            return {"total_stats": "2", "offset": 0, "limit": 100,
                    "data": [{"lead_email": "B@x.com", "is_bounced": True},
                             {"lead_email": "a@x.com", "is_bounced": False}]}
        raise AssertionError(f"unexpected GET {path}")


class EndToEndTest(unittest.TestCase):
    def run_main(self, *argv):
        out = Path(tempfile.mkdtemp())
        original = sa.Smartlead
        sa.Smartlead = FakeSmartlead
        os.environ["SMARTLEAD_API_KEY"] = "test-key"
        try:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = sa.main([*argv, "--out", str(out)])
        finally:
            sa.Smartlead = original
            del os.environ["SMARTLEAD_API_KEY"]
        self.assertEqual(code, 0)
        return out, buf.getvalue()

    def read(self, path):
        with path.open(newline="") as f:
            return list(csv.DictReader(f))

    def test_all(self):
        out, printed = self.run_main("all")
        accounts = {r["from_email"]: r for r in self.read(out / "accounts.csv")}
        self.assertEqual(set(accounts), {"leif@ja-team.com", "anna@ja-team.com",
                                         "old@ja-mail.com", "spare@ja-team.com"})
        self.assertEqual(accounts["leif@ja-team.com"]["verdict"], "READY")
        self.assertEqual(accounts["anna@ja-team.com"]["verdict"], "REST")
        self.assertEqual(accounts["old@ja-mail.com"]["verdict"], "RETIRE")
        self.assertEqual(accounts["old@ja-mail.com"]["provider"], "Microsoft")
        self.assertEqual(accounts["spare@ja-team.com"]["ja_campaigns"], "")  # included by tag
        self.assertIn("still in", printed)

        camps = {r["name"]: r for r in self.read(out / "campaigns.csv")}
        self.assertEqual(set(camps), {"JA / PT re-engage / Google / EN", "Joint Academy - PT old"})
        old = camps["Joint Academy - PT old"]
        self.assertEqual(old["bounce_rate_pct"], "5.0")
        self.assertIn("PAUSE: bounce over 3%", old["flags"])
        self.assertIn("UNFINISHED: 200 leads left", old["flags"])
        self.assertIn("1 inbox(es) not Ready", old["flags"])
        new = camps["JA / PT re-engage / Google / EN"]
        self.assertEqual(new["bounce_rate_pct"], "1.5")
        self.assertEqual(new["reply_rate_pct"], "2.0")
        self.assertIn("1 inbox(es) not Ready", new["flags"])  # anna is REST
        self.assertTrue((out / "domains.csv").exists())

    def test_all_accounts_and_client_filter(self):
        out, _ = self.run_main("accounts", "--all-accounts")
        self.assertEqual(len(self.read(out / "accounts.csv")), 6)

    def test_export_leads(self):
        out, _ = self.run_main("export-leads")
        files = sorted(out.glob("*.csv"))
        self.assertEqual([f.name for f in files],
                         ["10_JA_PT_re_engage_Google_EN.csv", "11_Joint_Academy_PT_old.csv"])
        rows = {r["email"]: r for r in self.read(files[0])}
        self.assertEqual(rows["b@x.com"]["is_bounced"], "true")
        self.assertEqual(rows["a@x.com"]["is_bounced"], "false")
        self.assertEqual(rows["a@x.com"]["campaign_name"], "JA / PT re-engage / Google / EN")

    def test_missing_key(self):
        os.environ.pop("SMARTLEAD_API_KEY", None)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(sa.main(["all"]), 2)


class RedactTest(unittest.TestCase):
    def test_key_redacted(self):
        sl = sa.Smartlead("secret123")
        self.assertEqual(sl._redact("url?api_key=secret123"), "url?api_key=***")


class ExportFeedsLeadFilterTest(unittest.TestCase):
    """The export's is_bounced column is what lead_filter reads."""

    def test_bounced_column_excludes(self):
        import lead_filter as lf
        tmp = Path(tempfile.mkdtemp())
        p = tmp / "exp.csv"
        p.write_text("email,status,title,company_name,reply_count,is_bounced,last_email_sequence_sent\n"
                     "a@x.com,COMPLETED,Physical Therapist,Bay PT,0,false,3\n"
                     "b@x.com,COMPLETED,Physical Therapist,Bay PT,0,true,1\n")
        lf.process([p], [], [], tmp / "out", use_mx=False, mx_cache=None)
        with (tmp / "out" / "reengage.csv").open() as f:
            self.assertEqual([r["email"] for r in csv.DictReader(f)], ["a@x.com"])


if __name__ == "__main__":
    unittest.main()
