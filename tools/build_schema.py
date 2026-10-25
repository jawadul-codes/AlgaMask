import csv, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from schema import TABLES, ENUMS, full_cols
root = pathlib.Path(__file__).parent.parent
for d in ["manifests","raw","staging","reviewed","fixtures","dictionaries","published"]:
    (root/"data"/d).mkdir(parents=True, exist_ok=True)
(root/"indexes"/"reviewed_evidence").mkdir(parents=True, exist_ok=True)

for t in TABLES:   # Create missing templates only; never erase populated data.
    path = root/"data/reviewed"/f"{t}.csv"
    if path.exists():
        continue
    with open(path,"x",newline="",encoding="utf-8") as f:
        csv.writer(f).writerow([c[0] for c in full_cols(t)])

with open(root/"data/dictionaries/columns.csv","w",newline="",encoding="utf-8") as f:
    w = csv.writer(f, lineterminator="\n"); w.writerow(["table","column","type","required","references_or_enum","description"])
    for t in TABLES:
        for n,ty,req,_,desc in full_cols(t):
            ref = ty.split(":",1)[1] if ":" in ty else ""
            w.writerow([t,n,ty.split(":")[0],req,ref,desc])
with open(root/"data/dictionaries/tables.csv","w",newline="",encoding="utf-8") as f:
    w = csv.writer(f, lineterminator="\n"); w.writerow(["table","primary_key","provenance_mode","description"])
    for t,m in TABLES.items(): w.writerow([t,m["pk"],m["prov"],m["desc"]])
with open(root/"data/dictionaries/enums.csv","w",newline="",encoding="utf-8") as f:
    w = csv.writer(f, lineterminator="\n"); w.writerow(["enum","value","description"])
    for e,vals in ENUMS.items():
        for v,d in vals: w.writerow([e,v,d])
manifest = root/"data/manifests/source_manifest.csv"
if not manifest.exists():
    with open(manifest,"x",newline="",encoding="utf-8") as f:
        csv.writer(f).writerow(["file_path","source_id","sha256","bytes","retrieved_at","licence","origin_url","committed_to_git"])
(root/"data/raw/.gitignore").write_text("*\n!.gitignore\n")
for d in ["staging","fixtures","published"]: (root/"data"/d/".gitkeep").touch()
(root/"indexes/reviewed_evidence/.gitkeep").touch()
print("built", len(TABLES), "tables")
