# viruspodden.se

Webbplats för **Viruspodden** – Sveriges första podcast om virus och virussjukdomar,
med Lennart Svensson och Åke Lundkvist.

Sidan hämtar alla avsnitt automatiskt från podcastens RSS-flöde på Podbean. När ett nytt
avsnitt publiceras på Podbean dyker det upp på viruspodden.se inom några timmar – ingen
behöver göra något på webbplatsen.

## Vad sidan innehåller

- **Startsida** – presentation, senaste avsnittet, fler avsnitt, om podden, programledarna och kontaktformulär
- **Alla avsnitt** (`/avsnitt/`) – hela arkivet, grupperat per år, med sökruta
- **En egen sida per avsnitt** (`/avsnitt/<namn>/`) – beskrivning, spelare, nedladdning, dela-knapp
- **Inbyggd spelare** – spola ±15/30 s, hastighet 0,75–2×, kommer ihåg var man slutade lyssna
- Länkar till Spotify, Apple Podcasts, Podbean m.fl. (visas när länkarna är ifyllda)
- Mobilanpassad, mörkt läge, sökmotoroptimerad (sitemap, delningsbilder, strukturerad data)
- Inga cookies och inga externa anrop förutom ljudfilerna från Podbean

## Så fungerar det

```
Podbean (RSS-flöde) ──► GitHub Actions kör build.py var 4:e timme ──► GitHub Pages ──► viruspodden.se
```

Ljudfilerna spelas direkt från Podbean, så lyssningarna räknas fortfarande i Podbeans statistik.

## Ändra texter och länkar

Allt innehåll som inte kommer från Podbean finns i **`site.json`**:

| Fält | Vad det är |
| --- | --- |
| `feed_url` | Podbeans RSS-adress, t.ex. `https://feed.podbean.com/viruspodden/feed.xml` |
| `tagline`, `intro`, `about` | Texterna på startsidan |
| `platforms` | Länkar till podden på Spotify, Apple Podcasts, YouTube, Amazon Music, Podbean. Tomma fält döljs. |
| `contact.email` | E-postadress som visas på sidan |
| `contact.form_endpoint`, `contact.form_access_key` | Kopplar kontaktformuläret till en e-posttjänst (se nedan) |
| `hosts` | Namn, titel och biografi för programledarna |

Ändrar man `site.json` direkt på GitHub (pennikonen) byggs och publiceras sidan om automatiskt.

### Utseende och bilder

Färger och typsnitt följer poddens omslag: blå bakgrund, turkos accent, Bebas Neue i rubriker
och Open Sans i brödtext. Omslaget hämtas automatiskt från Podbean. Bilden på programledarna
(`static/img/programledare.jpg`) är beskuren från omslaget och kan bytas mot ett annat foto.

Vill man ha separata porträtt läggs de som `static/img/lennart-svensson.jpg` och
`static/img/ake-lundkvist.jpg` (kvadratiska, minst 400×400 px).

### Kontaktformuläret

En statisk webbplats kan inte skicka e-post själv, så formuläret använder en gratistjänst.
Enklast är [Web3Forms](https://web3forms.com) (250 meddelanden/månad gratis, inget konto):

1. Gå till web3forms.com, skriv in e-postadressen som ska ta emot meddelandena och hämta en *Access Key*.
2. Fyll i `site.json`:
   ```json
   "contact": {
     "email": "",
     "form_endpoint": "https://api.web3forms.com/submit",
     "form_access_key": "din-access-key"
   }
   ```

[Formspree](https://formspree.io) fungerar också: sätt `form_endpoint` till din Formspree-adress
(`https://formspree.io/f/...`) och lämna `form_access_key` tom.

Är bara `email` ifyllt öppnar formuläret besökarens e-postprogram istället.
Är ingenting ifyllt visar formuläret att det inte är aktiverat ännu.

## Publicera på GitHub Pages med domänen från GoDaddy

1. **Repo:** lägg innehållet i den här mappen i roten av ett eget, publikt GitHub-repo (t.ex. `viruspodden`).
2. **Pages:** i repot, gå till *Settings → Pages* och välj *Source: GitHub Actions*.
   Arbetsflödet `.github/workflows/deploy.yml` bygger och publicerar sedan sidan automatiskt.
3. **Egen domän:** under *Settings → Pages → Custom domain*, skriv `viruspodden.se` och spara.
4. **DNS hos GoDaddy** (*Mina produkter → viruspodden.se → DNS*):
   - Ta bort befintliga `A`-poster för `@` (GoDaddys parkeringssida) och eventuell vidarebefordran.
   - Lägg till fyra `A`-poster för `@`:
     `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - Lägg till en `CNAME`-post: namn `www`, värde `<ditt-github-användarnamn>.github.io`
5. Vänta tills DNS slagit igenom (ofta under en timme, ibland upp till ett dygn) och kryssa sedan i
   *Enforce HTTPS* under *Settings → Pages*.

Tips: verifiera domänen under GitHub-kontots *Settings → Pages → Verified domains* så att ingen
annan kan använda den.

## Förhandsgranska lokalt

Kräver bara Python 3 (inga paket behövs).

```bash
python3 build.py --sample        # exempeldata, fungerar utan internet
python3 build.py                 # riktiga avsnitt från Podbean
python3 -m http.server -d _site 8000
```

Öppna sedan http://localhost:8000.

## Filer

```
site.json                 Texter, länkar och inställningar
build.py                  Hämtar RSS-flödet och bygger sajten till _site/
static/style.css          Utseende
static/app.js             Spelare, sök, meny, kontaktformulär
static/fonts/             Typsnitt (Bebas Neue och Open Sans, SIL Open Font License)
static/img/               Omslaget och bilden på programledarna
sample/                   Exempeldata för förhandsgranskning
.github/workflows/        Automatisk byggning och publicering
```
