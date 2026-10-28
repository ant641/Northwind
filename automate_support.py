#!/usr/bin/env python3
import csv, json, sys
from collections import Counter, defaultdict
from pathlib import Path

AUTO = {"Thumbnail re-upload": 5, "Login issue": 3, "Account access": 5}
REQUIRED = ["Ticket_ID","Date","Category","Submitted_By","Assigned_To","Handle_Minutes","Status"]

def main(src, outdir):
    out=Path(outdir); out.mkdir(parents=True, exist_ok=True)
    with open(src, newline='', encoding='utf-8-sig') as f:
        r=csv.DictReader(f)
        if r.fieldnames != REQUIRED: raise SystemExit(f"Bad schema: expected {REQUIRED}; got {r.fieldnames}")
        rows=list(r)
    routed=[]; before=after=0; counts=Counter(); savings=defaultdict(int)
    for x in rows:
        mins=int(x['Handle_Minutes']); before+=mins; counts[x['Category']]+=1
        new=AUTO.get(x['Category'], mins); after+=new; savings[x['Category']]+=mins-new
        y=dict(x); y['Automation_Action']='AUTO_RESOLVE' if x['Category'] in AUTO else 'HUMAN_REVIEW'
        y['Estimated_After_Minutes']=new; y['Estimated_Minutes_Saved']=mins-new
        routed.append(y)
    fields=REQUIRED+['Automation_Action','Estimated_After_Minutes','Estimated_Minutes_Saved']
    with open(out/'routed_tickets.csv','w',newline='') as f:
        w=csv.DictWriter(f,fields); w.writeheader(); w.writerows(routed)
    report={"tickets":len(rows),"baseline_minutes":before,"after_minutes":after,"minutes_saved":before-after,
            "reduction_pct":round((before-after)/before*100,1) if before else 0,
            "assumption":"After-times are explicit pilot assumptions, not observed production times.",
            "source":"support_tickets_q1_2026.csv rows; columns Ticket_ID, Category, Handle_Minutes, Status"}
    (out/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report, indent=2))
if __name__=='__main__':
    main(sys.argv[1] if len(sys.argv)>1 else 'support_tickets_q1_2026.csv', sys.argv[2] if len(sys.argv)>2 else 'output')
