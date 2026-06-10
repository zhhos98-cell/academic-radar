import csv, datetime, time, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import feedparser, requests

OPML_IN = "feedly.opml"
AUDIT_CSV = "feed_audit.csv"
ACTIVE_OPML = "feedly_active.opml"
STALE_OPML = "feedly_stale_or_unknown.opml"
CUTOFF_DAYS = 120  # 4 months-ish; change to 180 for 6 months
NOW = datetime.datetime.now(datetime.timezone.utc)

root = ET.parse(OPML_IN).getroot()
feeds = []
for outline in root.findall('.//outline'):
    url = outline.attrib.get('xmlUrl') or outline.attrib.get('xmlurl')
    if url:
        feeds.append({
            'title': outline.attrib.get('title') or outline.attrib.get('text') or url,
            'url': url,
        })

def entry_date(e):
    for key in ('published_parsed', 'updated_parsed', 'created_parsed'):
        val = e.get(key)
        if val:
            return datetime.datetime.fromtimestamp(time.mktime(val), tz=datetime.timezone.utc)
    for key in ('published', 'updated', 'created', 'date'):
        val = e.get(key)
        if val:
            try:
                dt = parsedate_to_datetime(val)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=datetime.timezone.utc)
                return dt.astimezone(datetime.timezone.utc)
            except Exception:
                pass
    return None

def check(feed):
    title, url = feed['title'], feed['url']
    try:
        r = requests.get(url, headers={'User-Agent': 'academic-radar/1.0'}, timeout=(5, 15))
        d = feedparser.parse(r.content)
        dates = [entry_date(e) for e in d.entries[:30]]
        dates = [x for x in dates if x]
        latest = max(dates) if dates else None
        age = (NOW - latest).days if latest else None
        return {
            'title': title,
            'url': url,
            'status': r.status_code,
            'entries_seen': len(d.entries),
            'latest': latest.isoformat() if latest else '',
            'age_days': age if age is not None else '',
            'decision': 'keep' if age is not None and age <= CUTOFF_DAYS else 'review_or_remove',
            'sample': ' | '.join((e.get('title', '')[:120] for e in d.entries[:3])),
            'error': '' if r.ok else f'HTTP {r.status_code}',
        }
    except Exception as ex:
        return {
            'title': title, 'url': url, 'status': '', 'entries_seen': 0,
            'latest': '', 'age_days': '', 'decision': 'review_or_remove',
            'sample': '', 'error': type(ex).__name__ + ': ' + str(ex)[:180]
        }

results = []
with ThreadPoolExecutor(max_workers=12) as pool:
    for fut in as_completed([pool.submit(check, f) for f in feeds]):
        results.append(fut.result())

results.sort(key=lambda r: (r['decision'], int(r['age_days']) if str(r['age_days']).isdigit() else 999999, r['title']))
with open(AUDIT_CSV, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['decision','title','url','status','entries_seen','latest','age_days','sample','error'])
    w.writeheader(); w.writerows(results)

keep_urls = {r['url'] for r in results if r['decision'] == 'keep'}
review_urls = {r['url'] for r in results if r['decision'] != 'keep'}

def write_opml(path, urls, title):
    opml = ET.Element('opml', version='2.0')
    head = ET.SubElement(opml, 'head'); ET.SubElement(head, 'title').text = title
    body = ET.SubElement(opml, 'body')
    for f in feeds:
        if f['url'] in urls:
            ET.SubElement(body, 'outline', text=f['title'], title=f['title'], type='rss', xmlUrl=f['url'])
    ET.ElementTree(opml).write(path, encoding='utf-8', xml_declaration=True)

write_opml(ACTIVE_OPML, keep_urls, 'Academic Radar active feeds')
write_opml(STALE_OPML, review_urls, 'Academic Radar stale or unknown feeds')
print(f"Audited {len(results)} feeds. Keep: {len(keep_urls)}. Review/remove: {len(review_urls)}.")
