#!/usr/bin/env python3
"""Apply source verification for formal distress event dates.

This script records source evidence for every formal distress event used by the
strict legal-distress benchmark and updates the event-date config so P0 audits
can distinguish verified event provenance from ordinary panel-coverage notes.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"
REPORT_DIR = PROJECT_ROOT / "reports/data_quality"

EVENT_CONFIG = CONFIG_DIR / "distress_event_dates.csv"
PROVENANCE_CONFIG = CONFIG_DIR / "distress_event_source_provenance.csv"
SUMMARY_CSV = REPORT_DIR / "distress_event_source_verification_summary_20260507.csv"
SUMMARY_MD = REPORT_DIR / "distress_event_source_verification_summary_20260507.md"

VERIFIED_STATUS = "source_verified_2026_05_07"


SOURCE_ROWS = [
    {
        "ticker": "AAMRQ",
        "company_name": "AMR Corporation / American Airlines",
        "event_date": "2011-11-29",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "American Airlines investor relations press release",
        "source_type": "company_press_release",
        "source_url": "https://americanairlines.gcs-web.com/news-releases/news-release-details/amr-and-american-airlines-file-chapter-11-reorganization-achieve",
        "court_or_regulator": "U.S. Bankruptcy Court for the Southern District of New York",
        "evidence_note": "AMR and U.S.-based subsidiaries announced voluntary Chapter 11 petitions on November 29, 2011.",
        "why_included": "Voluntary Chapter 11 filing is a formal legal distress event.",
        "limitations": "Ticker is the post-bankruptcy/OTC display identifier used in the panel.",
    },
    {
        "ticker": "ANRZQ",
        "company_name": "Alpha Natural Resources",
        "event_date": "2015-08-03",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "Alpha Natural Resources / PRNewswire release mirror",
        "source_type": "company_press_release_mirror",
        "source_url": "https://www.rohstoff-welt.de/weiterleitung_artikel.php?lang=en&sid=117767",
        "court_or_regulator": "U.S. Bankruptcy Court for the Eastern District of Virginia",
        "evidence_note": "Alpha Natural Resources and subsidiaries filed voluntary Chapter 11 petitions on August 3, 2015.",
        "why_included": "Voluntary Chapter 11 filing is a formal legal distress event.",
        "limitations": "Direct company archive was not accessible; the release is preserved through a PRNewswire mirror and corroborated by later Alpha restructuring releases.",
    },
    {
        "ticker": "ASNA",
        "company_name": "Ascena Retail Group",
        "event_date": "2020-07-23",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "Ascena SEC Form 10-K disclosure",
        "source_type": "sec_filing",
        "source_url": "https://www.sec.gov/Archives/edgar/data/1498301/000149830120000105/asna-20200801.htm",
        "court_or_regulator": "U.S. Bankruptcy Court for the Eastern District of Virginia",
        "evidence_note": "Ascena disclosed that it and subsidiaries commenced voluntary Chapter 11 cases on July 23, 2020.",
        "why_included": "Voluntary Chapter 11 filing is a formal legal distress event.",
        "limitations": "SEC filing is a later periodic report, not the initial press release.",
    },
    {
        "ticker": "BBBY",
        "company_name": "Bed Bath & Beyond",
        "event_date": "2023-04-23",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "Bed Bath & Beyond / PRNewswire press release",
        "source_type": "company_press_release",
        "source_url": "https://www.prnewswire.com/news-releases/bed-bath--beyond-inc-files-voluntary-chapter-11-petitions-301804829.html",
        "court_or_regulator": "U.S. Bankruptcy Court for the District of New Jersey",
        "evidence_note": "The company announced voluntary Chapter 11 petitions on April 23, 2023.",
        "why_included": "Voluntary Chapter 11 filing is a formal legal distress event.",
        "limitations": "None beyond ordinary bankruptcy-source reporting limits.",
    },
    {
        "ticker": "BRDS",
        "company_name": "Bird Global",
        "event_date": "2023-12-20",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "Associated Press report",
        "source_type": "reputable_newswire",
        "source_url": "https://apnews.com/article/b1c48aca963ba163160e2b610a1eb870",
        "court_or_regulator": "U.S. Bankruptcy Court in Florida",
        "evidence_note": "AP reported that Bird Global filed for Chapter 11 bankruptcy protection on December 20, 2023.",
        "why_included": "Chapter 11 filing is a formal legal distress event.",
        "limitations": "Official company release was not found in the accessible search results; reputable newswire source used.",
    },
    {
        "ticker": "BTUUQ",
        "company_name": "Peabody Energy",
        "event_date": "2016-04-13",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "Peabody Energy / PRNewswire press release",
        "source_type": "company_press_release",
        "source_url": "https://www.prnewswire.com/news-releases/amid-prolonged-industry-downturn-peabody-energy-takes-major-step-to-strengthen-liquidity-and-reduce-debt-through-chapter-11-protection-300250678.html",
        "court_or_regulator": "U.S. Bankruptcy Court for the Eastern District of Missouri",
        "evidence_note": "Peabody announced voluntary Chapter 11 petitions for the majority of its U.S. entities on April 13, 2016.",
        "why_included": "Voluntary Chapter 11 filing is a formal legal distress event.",
        "limitations": "Australian entities were excluded from the filing.",
    },
    {
        "ticker": "CANO",
        "company_name": "Cano Health",
        "event_date": "2024-02-04",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "Cano Health / PRNewswire press release",
        "source_type": "company_press_release",
        "source_url": "https://www.prnewswire.com/news-releases/cano-health-enters-restructuring-support-agreement-with-a-significant-majority-of-its-lenders-to-strengthen-financial-position-302052889.html",
        "court_or_regulator": "U.S. Bankruptcy Court for the District of Delaware",
        "evidence_note": "Cano Health announced a restructuring support agreement and Chapter 11 implementation on February 4, 2024.",
        "why_included": "Chapter 11 restructuring is a formal legal distress event.",
        "limitations": "The press release emphasizes the restructuring agreement; later SEC filings corroborate the Chapter 11 proceedings.",
    },
    {
        "ticker": "CHK",
        "company_name": "Chesapeake Energy",
        "event_date": "2020-06-28",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "Chesapeake Energy / PRNewswire press release",
        "source_type": "company_press_release",
        "source_url": "https://www.prnewswire.com/news-releases/chesapeake-energy-corporation-commences-voluntary-chapter-11-process-301084764.html",
        "court_or_regulator": "U.S. Bankruptcy Court for the Southern District of Texas",
        "evidence_note": "Chesapeake announced voluntary Chapter 11 filing on June 28, 2020.",
        "why_included": "Voluntary Chapter 11 filing is a formal legal distress event.",
        "limitations": "None beyond ordinary bankruptcy-source reporting limits.",
    },
    {
        "ticker": "CIT",
        "company_name": "CIT Group",
        "event_date": "2009-11-01",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "CIT Group SEC Form 8-K",
        "source_type": "sec_filing",
        "source_url": "https://www.sec.gov/Archives/edgar/data/1171825/000095012309057703/y80157e8vk.htm",
        "court_or_regulator": "U.S. Bankruptcy Court for the Southern District of New York",
        "evidence_note": "CIT disclosed voluntary Chapter 11 petitions filed on November 1, 2009.",
        "why_included": "Voluntary Chapter 11 filing is a formal legal distress event.",
        "limitations": "Event predates the first usable panel prediction rows, so it contributes post-event metadata rather than forward labels.",
    },
    {
        "ticker": "EKDKQ",
        "company_name": "Eastman Kodak",
        "event_date": "2012-01-19",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "ABC News report citing Kodak news release",
        "source_type": "reputable_news_report",
        "source_url": "https://abcnews.go.com/blogs/business/2012/01/kodak-files-for-chapter-11-bankruptcy",
        "court_or_regulator": "U.S. Bankruptcy Court for the Southern District of New York",
        "evidence_note": "ABC reported, citing Kodak's release, that Kodak and U.S. subsidiaries filed voluntary Chapter 11 petitions on January 19, 2012.",
        "why_included": "Voluntary Chapter 11 filing is a formal legal distress event.",
        "limitations": "Official Kodak archive was not accessible in the search results; reputable reporting cites the company release.",
    },
    {
        "ticker": "FTR",
        "company_name": "Frontier Communications",
        "event_date": "2020-04-14",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "Frontier Communications investor relations release",
        "source_type": "company_press_release",
        "source_url": "https://investor.frontier.com/news/news-details/2020/Frontier-Communications-Receives-Court-Approval-of-All-First-Day-Motions-to-Support-Business-Operations-04-16-2020/default.aspx",
        "court_or_regulator": "U.S. Bankruptcy Court for the Southern District of New York",
        "evidence_note": "Frontier disclosed voluntary Chapter 11 petitions filed on April 14, 2020.",
        "why_included": "Voluntary Chapter 11 filing is a formal legal distress event.",
        "limitations": "Source is a first-day approval release two days after the petition date.",
    },
    {
        "ticker": "GTATQ",
        "company_name": "GT Advanced Technologies",
        "event_date": "2014-10-06",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "GT Advanced Technologies SEC exhibit press release",
        "source_type": "sec_filing",
        "source_url": "https://www.sec.gov/Archives/edgar/data/1394954/000144530514004279/gtat10102014pressreleaseex.htm",
        "court_or_regulator": "U.S. Bankruptcy Court for the District of New Hampshire",
        "evidence_note": "The SEC-filed press release states GT and subsidiaries commenced Chapter 11 cases on October 6, 2014.",
        "why_included": "Voluntary Chapter 11 filing is a formal legal distress event.",
        "limitations": "None beyond ordinary bankruptcy-source reporting limits.",
    },
    {
        "ticker": "HTZ",
        "company_name": "Hertz Global Holdings",
        "event_date": "2020-05-22",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "Hertz newsroom press release",
        "source_type": "company_press_release",
        "source_url": "https://newsroom.hertz.com/press-releases/press-release-details/hertz-global-holdings-takes-action-to-strengthen-capital-structure-following-impact-of-glo/",
        "court_or_regulator": "U.S. Bankruptcy Court for the District of Delaware",
        "evidence_note": "Hertz announced that it and certain U.S. and Canadian subsidiaries filed Chapter 11 petitions on May 22, 2020.",
        "why_included": "Voluntary Chapter 11 filing is a formal legal distress event.",
        "limitations": "The release page is dated May 23 but states the May 22 filing date.",
    },
    {
        "ticker": "JCP",
        "company_name": "J. C. Penney",
        "event_date": "2020-05-15",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "JCPenney newsroom press release",
        "source_type": "company_press_release",
        "source_url": "https://corporate.jcpenney.com/2020/05/15/jcpenney-to-reduce-debt-and-strengthen-financial-position-through-restructuring-support-agreement/",
        "court_or_regulator": "U.S. Bankruptcy Court for the Southern District of Texas",
        "evidence_note": "JCPenney announced voluntary Chapter 11 petitions filed on May 15, 2020.",
        "why_included": "Voluntary Chapter 11 filing is a formal legal distress event.",
        "limitations": "None beyond ordinary bankruptcy-source reporting limits.",
    },
    {
        "ticker": "JOAN",
        "company_name": "JOANN",
        "event_date": "2024-03-18",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "JOANN / GlobeNewswire release via Nasdaq",
        "source_type": "company_press_release_mirror",
        "source_url": "https://www.nasdaq.com/press-release/joann-enters-into-agreement-to-reduce-debt-and-receive-%24132-million-in-new-capital",
        "court_or_regulator": "U.S. Bankruptcy Court",
        "evidence_note": "JOANN announced a financial restructuring transaction and Chapter 11 process on March 18, 2024.",
        "why_included": "Chapter 11 filing is a formal legal distress event.",
        "limitations": "Source is a Nasdaq-hosted copy of the GlobeNewswire/company release.",
    },
    {
        "ticker": "LINEQ",
        "company_name": "LINN Energy",
        "event_date": "2016-05-11",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "LINN Energy SEC registration statement",
        "source_type": "sec_filing",
        "source_url": "https://www.sec.gov/Archives/edgar/data/1326428/000119312517294444/d386160ds1a.htm",
        "court_or_regulator": "U.S. Bankruptcy Court for the Southern District of Texas",
        "evidence_note": "The SEC filing states LINN and affiliates filed voluntary Chapter 11 petitions on May 11, 2016.",
        "why_included": "Voluntary Chapter 11 filing is a formal legal distress event.",
        "limitations": "SEC filing is a later registration statement, not the initial release.",
    },
    {
        "ticker": "NPCMQ",
        "company_name": "Noble Corporation",
        "event_date": "2020-07-31",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "Noble Corporation investor relations release",
        "source_type": "company_press_release",
        "source_url": "https://www.noblecorp.com/investors/news/news-details/2020/Noble-Corporation-plc-Announces-Comprehensive-Financial-Restructuring-And-Deleveraging-Transaction/default.aspx",
        "court_or_regulator": "U.S. Bankruptcy Court for the Southern District of Texas",
        "evidence_note": "Noble announced a voluntary Chapter 11 restructuring process on July 31, 2020.",
        "why_included": "Voluntary Chapter 11 filing is a formal legal distress event.",
        "limitations": "The row ticker is the panel's distressed/OTC display identifier.",
    },
    {
        "ticker": "PGNPQ",
        "company_name": "PG&E Corporation",
        "event_date": "2019-01-29",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "PG&E investor relations press release",
        "source_type": "company_press_release",
        "source_url": "https://investor.pgecorp.com/news-events/press-releases/press-release-details/2019/PGE-Files-for-Reorganization-Under-Chapter-11/default.aspx?print=1",
        "court_or_regulator": "U.S. Bankruptcy Court for the Northern District of California",
        "evidence_note": "PG&E announced voluntary Chapter 11 petitions filed on January 29, 2019.",
        "why_included": "Voluntary Chapter 11 filing is a formal legal distress event.",
        "limitations": "Ticker is the distressed/OTC display identifier used in the panel.",
    },
    {
        "ticker": "PIRRQ",
        "company_name": "Pier 1 Imports",
        "event_date": "2020-02-17",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "Pier 1 / Business Wire release via Nasdaq",
        "source_type": "company_press_release_mirror",
        "source_url": "https://www.nasdaq.com/press-release/pier-1-enters-plan-support-agreement-with-certain-lenders-and-announces-sale-process",
        "court_or_regulator": "U.S. Bankruptcy Court for the Eastern District of Virginia",
        "evidence_note": "Pier 1 announced voluntary Chapter 11 proceedings on February 17, 2020.",
        "why_included": "Voluntary Chapter 11 filing is a formal legal distress event.",
        "limitations": "Source is a Nasdaq-hosted copy of the company/Business Wire release.",
    },
    {
        "ticker": "PRTY",
        "company_name": "Party City Holdco",
        "event_date": "2023-01-17",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "Party City SEC Form 8-K",
        "source_type": "sec_filing",
        "source_url": "https://www.sec.gov/Archives/edgar/data/1592058/000119312523009847/d643228d8k.htm",
        "court_or_regulator": "U.S. Bankruptcy Court for the Southern District of Texas",
        "evidence_note": "Party City disclosed voluntary Chapter 11 petitions filed on January 17, 2023.",
        "why_included": "Voluntary Chapter 11 filing is a formal legal distress event.",
        "limitations": "None beyond ordinary bankruptcy-source reporting limits.",
    },
    {
        "ticker": "PTRA",
        "company_name": "Proterra",
        "event_date": "2023-08-07",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "Proterra SEC exhibit press release",
        "source_type": "sec_filing",
        "source_url": "https://www.sec.gov/Archives/edgar/data/1820630/000162828023027865/a8x7x23ex991pressreleaseda.htm",
        "court_or_regulator": "U.S. Bankruptcy Court for the District of Delaware",
        "evidence_note": "Proterra's SEC-filed release states the company voluntarily filed for Chapter 11 on August 7, 2023.",
        "why_included": "Voluntary Chapter 11 filing is a formal legal distress event.",
        "limitations": "None beyond ordinary bankruptcy-source reporting limits.",
    },
    {
        "ticker": "REV",
        "company_name": "Revlon",
        "event_date": "2022-06-15",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "Revlon / Business Wire earnings release",
        "source_type": "company_press_release",
        "source_url": "https://www.businesswire.com/news/home/20221107006168/en/Revlon-Reports-Third-Quarter-2022-Results",
        "court_or_regulator": "U.S. Bankruptcy Court for the Southern District of New York",
        "evidence_note": "Revlon stated that it and certain subsidiaries filed voluntary Chapter 11 petitions on June 15, 2022.",
        "why_included": "Voluntary Chapter 11 filing is a formal legal distress event.",
        "limitations": "Source is a later company earnings release discussing the pending Chapter 11 cases.",
    },
    {
        "ticker": "RIDE",
        "company_name": "Lordstown Motors",
        "event_date": "2023-06-27",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "Lordstown Motors investor relations press release",
        "source_type": "company_press_release",
        "source_url": "https://investor.lordstownmotors.com/news-releases/news-release-details/lordstown-motors-announces-strategic-restructuring-process/",
        "court_or_regulator": "U.S. Bankruptcy Court for the District of Delaware",
        "evidence_note": "Lordstown announced Chapter 11 filing on June 27, 2023.",
        "why_included": "Chapter 11 filing is a formal legal distress event.",
        "limitations": "None beyond ordinary bankruptcy-source reporting limits.",
    },
    {
        "ticker": "SDC",
        "company_name": "SmileDirectClub",
        "event_date": "2023-09-29",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "Law360 bankruptcy case summary",
        "source_type": "professional_bankruptcy_report",
        "source_url": "https://www.law360.com/bankruptcy-authority/articles/1727966/smiledirectclub-gets-30m-ch-11-loan-package",
        "court_or_regulator": "U.S. Bankruptcy Court for the Southern District of Texas",
        "evidence_note": "The bankruptcy report identifies SmileDirectClub's Chapter 11 case and September 29, 2023 filing date.",
        "why_included": "Chapter 11 filing is a formal legal distress event.",
        "limitations": "Detailed article access may be limited; public search result provides the case date and venue.",
    },
    {
        "ticker": "SHLDQ",
        "company_name": "Sears Holdings",
        "event_date": "2018-10-15",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "Sears Holdings / Transformco press release",
        "source_type": "company_press_release",
        "source_url": "https://www.searsholdings.com/press-releases/pr/2116",
        "court_or_regulator": "U.S. Bankruptcy Court for the Southern District of New York",
        "evidence_note": "Sears Holdings announced voluntary Chapter 11 proceedings on October 15, 2018.",
        "why_included": "Voluntary Chapter 11 filing is a formal legal distress event.",
        "limitations": "None beyond ordinary bankruptcy-source reporting limits.",
    },
    {
        "ticker": "SI",
        "company_name": "Silvergate Capital / Silvergate Bank",
        "event_date": "2023-03-08",
        "event_type": "liquidation_distress",
        "event_label": "formal_distress",
        "source_name": "Federal Reserve enforcement press release",
        "source_type": "regulator_release",
        "source_url": "https://www.federalreserve.gov/newsevents/pressreleases/enforcement20230601a.htm",
        "court_or_regulator": "Federal Reserve Board and California DFPI",
        "evidence_note": "The Federal Reserve described Silvergate's voluntary self-liquidation announced on March 8, 2023.",
        "why_included": "Regulator-confirmed bank self-liquidation is treated as formal distress, but not as Chapter 11.",
        "limitations": "This is not a bankruptcy filing; it is a regulated bank wind-down/liquidation event.",
    },
    {
        "ticker": "SIVB",
        "company_name": "Silicon Valley Bank",
        "event_date": "2023-03-10",
        "event_type": "bank_failure",
        "event_label": "formal_distress",
        "source_name": "FDIC failed bank information page",
        "source_type": "regulator_release",
        "source_url": "https://www.fdic.gov/resources/resolutions/bank-failures/failed-bank-list/silicon-valley.html",
        "court_or_regulator": "California DFPI / FDIC",
        "evidence_note": "FDIC states Silicon Valley Bank was closed on March 10, 2023 and FDIC was named receiver.",
        "why_included": "Regulator-confirmed bank failure is a formal legal distress event.",
        "limitations": "This is a bank receivership/failure, not a Chapter 11 bankruptcy.",
    },
    {
        "ticker": "SUNEQ",
        "company_name": "SunEdison",
        "event_date": "2016-04-21",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "SunEdison / PRNewswire press release",
        "source_type": "company_press_release",
        "source_url": "https://www.prnewswire.com/news-releases/sunedison-undertakes-chapter-11-reorganization-300255363.html",
        "court_or_regulator": "U.S. Bankruptcy Court for the Southern District of New York",
        "evidence_note": "SunEdison announced voluntary Chapter 11 petitions on April 21, 2016.",
        "why_included": "Voluntary Chapter 11 filing is a formal legal distress event.",
        "limitations": "TerraForm yieldcos were not part of the filing.",
    },
    {
        "ticker": "TOYRF",
        "company_name": "Toys R Us",
        "event_date": "2017-09-18",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "Toys R Us / PRNewswire press release",
        "source_type": "company_press_release",
        "source_url": "https://www.prnewswire.com/news-releases/toysrus-inc-commences-court-supervised-processes-to-implement-financial-restructuring-300521734.html",
        "court_or_regulator": "U.S. Bankruptcy Court for the Eastern District of Virginia",
        "evidence_note": "Toys R Us announced Chapter 11 petitions in the U.S. on September 18, 2017.",
        "why_included": "Voluntary Chapter 11 filing is a formal legal distress event.",
        "limitations": "Canadian proceedings were parallel CCAA proceedings; non-U.S./Canada operations were excluded.",
    },
    {
        "ticker": "TUES",
        "company_name": "Tuesday Morning",
        "event_date": "2020-05-27",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "Tuesday Morning / GlobeNewswire press release",
        "source_type": "company_press_release",
        "source_url": "https://www.globenewswire.com/news-release/2020/05/27/2039197/0/en/Tuesday-Morning-Corporation-Files-Chapter-11-to-Pursue-Financial-and-Operational-Reorganization.html",
        "court_or_regulator": "U.S. Bankruptcy Court",
        "evidence_note": "Tuesday Morning announced Chapter 11 filing on May 27, 2020.",
        "why_included": "Voluntary Chapter 11 filing is a formal legal distress event.",
        "limitations": "None beyond ordinary bankruptcy-source reporting limits.",
    },
    {
        "ticker": "TUP",
        "company_name": "Tupperware Brands",
        "event_date": "2024-09-17",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "Tupperware / PRNewswire press release",
        "source_type": "company_press_release",
        "source_url": "https://www.prnewswire.com/news-releases/tupperware-voluntarily-initiates-chapter-11-proceedings-302251267.html",
        "court_or_regulator": "U.S. Bankruptcy Court for the District of Delaware",
        "evidence_note": "Tupperware announced voluntary Chapter 11 proceedings on September 17, 2024.",
        "why_included": "Voluntary Chapter 11 filing is a formal legal distress event.",
        "limitations": "None beyond ordinary bankruptcy-source reporting limits.",
    },
    {
        "ticker": "UCIHQ",
        "company_name": "Ultra Petroleum",
        "event_date": "2016-04-29",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "Ultra Petroleum SEC registration statement",
        "source_type": "sec_filing",
        "source_url": "https://www.sec.gov/Archives/edgar/data/1022646/000119312517139781/d372819ds1.htm",
        "court_or_regulator": "U.S. Bankruptcy Court for the Southern District of Texas",
        "evidence_note": "Ultra disclosed voluntary Chapter 11 petitions filed on April 29, 2016.",
        "why_included": "Voluntary Chapter 11 filing is a formal legal distress event.",
        "limitations": "SEC filing is a later registration statement, not the initial release.",
    },
    {
        "ticker": "WE",
        "company_name": "WeWork",
        "event_date": "2023-11-06",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "WeWork SEC Form 10-Q disclosure",
        "source_type": "sec_filing",
        "source_url": "https://www.sec.gov/Archives/edgar/data/0001813756/000181375623000067/wework2023q310q.htm",
        "court_or_regulator": "U.S. Bankruptcy Court for the District of New Jersey",
        "evidence_note": "WeWork disclosed voluntary Chapter 11 petitions filed on November 6, 2023.",
        "why_included": "Voluntary Chapter 11 filing is a formal legal distress event.",
        "limitations": "Chapter 11 cases were limited to U.S. and Canada locations.",
    },
    {
        "ticker": "WLL",
        "company_name": "Whiting Petroleum",
        "event_date": "2020-04-01",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "Whiting Petroleum / Business Wire release via Nasdaq",
        "source_type": "company_press_release_mirror",
        "source_url": "https://www.nasdaq.com/press-release/whiting-petroleum-corporation-reaches-agreement-in-principle-with-certain-of-its",
        "court_or_regulator": "U.S. Bankruptcy Court for the Southern District of Texas",
        "evidence_note": "Whiting announced voluntary Chapter 11 cases on April 1, 2020.",
        "why_included": "Voluntary Chapter 11 filing is a formal legal distress event.",
        "limitations": "Source is a Nasdaq-hosted copy of the company/Business Wire release.",
    },
    {
        "ticker": "WLTGQ",
        "company_name": "Walter Energy",
        "event_date": "2015-07-15",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "Walter Energy / PRNewswire restructuring release",
        "source_type": "company_press_release",
        "source_url": "https://www.prnewswire.com/news-releases/walter-energy-enters-into-asset-purchase-agreement-with-company-formed-by-its-senior-lender-group-300173575.html",
        "court_or_regulator": "U.S. Bankruptcy Court for the Northern District of Alabama",
        "evidence_note": "Walter Energy later confirmed that it and U.S. subsidiaries filed Chapter 11 on July 15, 2015.",
        "why_included": "Voluntary Chapter 11 filing is a formal legal distress event.",
        "limitations": "Source is a later company restructuring release confirming the filing date.",
    },
    {
        "ticker": "YELL",
        "company_name": "Yellow Corporation",
        "event_date": "2023-08-06",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "Yellow Corporation investor relations press release",
        "source_type": "company_press_release",
        "source_url": "https://investors.myyellow.com/news-releases/news-release-details/yellow-corporation-files-voluntary-chapter-11-petitions/",
        "court_or_regulator": "U.S. Bankruptcy Court for the District of Delaware",
        "evidence_note": "Yellow announced voluntary Chapter 11 petitions on August 6, 2023 for an operational wind-down.",
        "why_included": "Voluntary Chapter 11 filing and wind-down is a formal legal distress event.",
        "limitations": "None beyond ordinary bankruptcy-source reporting limits.",
    },
    {
        "ticker": "CIK0000084129",
        "company_name": "Rite Aid",
        "event_date": "2023-10-15",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "Rite Aid / Business Wire release via Nasdaq",
        "source_type": "company_press_release_mirror",
        "source_url": "https://www.nasdaq.com/press-release/rite-aid-takes-steps-to-accelerate-transformation-and-position-company-for-long-term",
        "court_or_regulator": "U.S. Bankruptcy Court",
        "evidence_note": "Rite Aid announced initiation of a voluntary Chapter 11 process on October 15, 2023.",
        "why_included": "Voluntary Chapter 11 filing is a formal legal distress event.",
        "limitations": "Config uses CIK identifier because this row came from CIK-based expansion matching.",
    },
    {
        "ticker": "CIK0000867773",
        "company_name": "SunPower",
        "event_date": "2024-08-05",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "SunPower / PRNewswire release via Nasdaq",
        "source_type": "company_press_release_mirror",
        "source_url": "https://www.nasdaq.com/press-release/sunpower-announces-stalking-horse-asset-purchase-agreement-complete-solaria-sell-blue",
        "court_or_regulator": "U.S. Bankruptcy Court for the District of Delaware",
        "evidence_note": "SunPower announced voluntary Chapter 11 petitions on August 5, 2024.",
        "why_included": "Voluntary Chapter 11 filing is a formal legal distress event.",
        "limitations": "Config uses CIK identifier because this row came from CIK-based expansion matching.",
    },
    {
        "ticker": "CIK0001008848",
        "company_name": "Acorda Therapeutics",
        "event_date": "2024-04-01",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "Acorda Therapeutics / Business Wire release via Nasdaq",
        "source_type": "company_press_release_mirror",
        "source_url": "https://www.nasdaq.com/press-release/acorda-therapeutics-and-merz-announce-signing-of-stalking-horse-asset-purchase",
        "court_or_regulator": "U.S. Bankruptcy Court for the Southern District of New York",
        "evidence_note": "Acorda announced voluntary Chapter 11 petitions on April 1, 2024.",
        "why_included": "Voluntary Chapter 11 filing is a formal legal distress event.",
        "limitations": "Config uses CIK identifier because this row came from CIK-based expansion matching.",
    },
    {
        "ticker": "CIK0000077281",
        "company_name": "PREIT",
        "event_date": "2023-12-10",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "PREIT restructuring page",
        "source_type": "company_restructuring_page",
        "source_url": "https://www.preit.com/restructuring/",
        "court_or_regulator": "U.S. Bankruptcy Court",
        "evidence_note": "PREIT states that on December 10, 2023 it announced a prepackaged Chapter 11 reorganization.",
        "why_included": "Voluntary Chapter 11 filing is a formal legal distress event.",
        "limitations": "Config uses CIK identifier because this row came from CIK-based expansion matching.",
    },
    {
        "ticker": "CIK0001223389",
        "company_name": "Conn's",
        "event_date": "2024-07-23",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "Sidley Austin Chapter 11 case announcement",
        "source_type": "professional_legal_report",
        "source_url": "https://www.sidley.com/en/newslanding/newsannouncements/2025/08/sidley-secures-confirmation-of-conn-chapter-11-plan",
        "court_or_regulator": "U.S. Bankruptcy Court for the Southern District of Texas",
        "evidence_note": "Sidley reports that Conn's filed for Chapter 11 bankruptcy protection on July 23, 2024.",
        "why_included": "Chapter 11 filing is a formal legal distress event.",
        "limitations": "Config uses CIK identifier; source is a professional legal report rather than the company press release.",
    },
    {
        "ticker": "CIK0000814549",
        "company_name": "Ebix",
        "event_date": "2023-12-17",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "Sidley Austin Chapter 11 case announcement",
        "source_type": "professional_legal_report",
        "source_url": "https://www.sidley.com/en/newslanding/newsannouncements/2024/08/sidley-secures-confirmation-of-ebix-chapter-11-plan",
        "court_or_regulator": "U.S. Bankruptcy Court for the Northern District of Texas",
        "evidence_note": "Sidley reports that Ebix filed for Chapter 11 bankruptcy on December 17, 2023.",
        "why_included": "Chapter 11 filing is a formal legal distress event.",
        "limitations": "Config uses CIK identifier; source is a professional legal report rather than the initial company release.",
    },
    {
        "ticker": "CIK0000890447",
        "company_name": "Vertex Energy",
        "event_date": "2024-09-24",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "U.S. EPA bankruptcy settlement summary",
        "source_type": "regulator_summary",
        "source_url": "https://www.epa.gov/enforcement/vertex-energy-inc-bankruptcy-and-environmental-settlement-summary",
        "court_or_regulator": "U.S. Bankruptcy Court for the Southern District of Texas",
        "evidence_note": "EPA states Vertex and affiliates filed voluntary Chapter 11 petitions on September 24, 2024.",
        "why_included": "Voluntary Chapter 11 filing is a formal legal distress event.",
        "limitations": "Config uses CIK identifier; source is a regulator settlement summary rather than the company release.",
    },
    {
        "ticker": "UNTC",
        "company_name": "Unit Corporation",
        "event_date": "2020-05-22",
        "event_type": "bankruptcy",
        "event_label": "formal_distress",
        "source_name": "Unit Corporation SEC exhibit press release",
        "source_type": "sec_filing",
        "source_url": "https://www.sec.gov/Archives/edgar/data/798949/000079894920000037/exhibit991pressrelease.htm",
        "court_or_regulator": "U.S. Bankruptcy Court for the Southern District of Texas",
        "evidence_note": "Unit's SEC-filed release states it filed voluntary Chapter 11 cases on May 22, 2020.",
        "why_included": "Voluntary Chapter 11 filing is a formal legal distress event.",
        "limitations": "None beyond ordinary bankruptcy-source reporting limits.",
    },
]


FIELDNAMES = [
    "ticker",
    "company_name",
    "event_date",
    "event_type",
    "event_label",
    "verification_status",
    "source_name",
    "source_type",
    "source_url",
    "court_or_regulator",
    "evidence_note",
    "why_included",
    "limitations",
    "verified_on",
]


def write_provenance() -> pd.DataFrame:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for row in SOURCE_ROWS:
        out = dict(row)
        out["verification_status"] = VERIFIED_STATUS
        out["verified_on"] = "2026-05-07"
        rows.append(out)

    with PROVENANCE_CONFIG.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    return pd.DataFrame(rows)


def update_event_config(provenance: pd.DataFrame) -> pd.DataFrame:
    events = pd.read_csv(EVENT_CONFIG)
    key_to_record = {
        (row["ticker"], row["event_date"]): row
        for row in provenance.to_dict(orient="records")
    }
    updated = 0
    for idx, event in events.iterrows():
        key = (str(event["ticker"]), str(event["event_date"]))
        record = key_to_record.get(key)
        if record is None:
            continue
        events.at[idx, "verification_status"] = VERIFIED_STATUS
        events.at[
            idx,
            "notes",
        ] = f"{record['company_name']} {record['event_type']} event date source-verified on 2026-05-07; see config/distress_event_source_provenance.csv."
        updated += 1

    events.to_csv(EVENT_CONFIG, index=False)

    summary_rows = [
        {"metric": "formal_source_records", "value": len(provenance)},
        {"metric": "config_rows_updated", "value": updated},
        {
            "metric": "formal_config_initial_seed_remaining",
            "value": int(
                (
                    events["event_label"].eq("formal_distress")
                    & events["verification_status"].eq("initial_seed")
                ).sum()
            ),
        },
        {
            "metric": "near_distress_initial_seed_context_rows",
            "value": int(
                (
                    events["event_label"].ne("formal_distress")
                    & events["verification_status"].eq("initial_seed")
                ).sum()
            ),
        },
    ]
    pd.DataFrame(summary_rows).to_csv(SUMMARY_CSV, index=False)

    source_type_counts = provenance["source_type"].value_counts().rename_axis("source_type").reset_index(name="rows")
    source_type_counts.to_csv(REPORT_DIR / "distress_event_source_type_counts_20260507.csv", index=False)

    text = [
        "# Distress Event Source Verification Summary",
        "",
        "Updated: 2026-05-07",
        "",
        f"- Formal distress event source records written: {len(provenance)}.",
        f"- Formal event rows updated in `config/distress_event_dates.csv`: {updated}.",
        f"- Formal `initial_seed` rows remaining: {summary_rows[2]['value']}.",
        f"- Non-strict near-distress context rows still marked `initial_seed`: {summary_rows[3]['value']}.",
        "",
        "The maintained source-evidence table is `config/distress_event_source_provenance.csv`.",
        "Non-strict near-distress rows are not used as formal legal distress labels.",
    ]
    SUMMARY_MD.write_text("\n".join(text) + "\n", encoding="utf-8")
    return events


def main() -> None:
    provenance = write_provenance()
    events = update_event_config(provenance)
    remaining = int(
        (
            events["event_label"].eq("formal_distress")
            & events["verification_status"].eq("initial_seed")
        ).sum()
    )
    print(f"Wrote {PROVENANCE_CONFIG.relative_to(PROJECT_ROOT)} rows={len(provenance)}")
    print(f"Updated {EVENT_CONFIG.relative_to(PROJECT_ROOT)}")
    print(f"Formal initial_seed rows remaining={remaining}")


if __name__ == "__main__":
    main()
