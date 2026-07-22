export const LONG_MONTHS  = [0,3,6,9,12,18,24,36];
export const ACCEL_MONTHS = [0,3,6];

export let db = {

products:[
{id:1,name:'Amoxicillin Capsules',strength:'500 mg',dosage:'Capsule',desc:'Broad-spectrum antibiotic',monographId:1},
{id:2,name:'Paracetamol Tablets',strength:'500 mg',dosage:'Tablet',desc:'Analgesic and antipyretic',monographId:2},
{id:3,name:'Omeprazole Capsules',strength:'20 mg',dosage:'Capsule',desc:'Proton pump inhibitor',monographId:1},
],

monographs:[
{id:1,name:'BP Monograph – Antibiotics',version:'2.1',date:'2024-01-01',status:'Active'},
{id:2,name:'BP Monograph – Analgesics',version:'1.3',date:'2024-03-15',status:'Active'},
{id:3,name:'USP General Monograph',version:'3.0',date:'2023-09-01',status:'Inactive'},
],

tests:[
{id:1,monographId:1,seq:1,name:'Assay',spec:'90.0 – 110.0%',method:'BP 2023 – HPLC'},
{id:2,monographId:1,seq:2,name:'Dissolution',spec:'NLT 80% in 45 min',method:'USP <711>'},
{id:3,monographId:1,seq:3,name:'Related Substances',spec:'NMT 0.5%',method:'BP 2023 – HPLC'},
{id:4,monographId:1,seq:4,name:'Water Content',spec:'NMT 4.0%',method:'Karl Fischer'},
{id:5,monographId:2,seq:1,name:'Assay',spec:'95.0 – 105.0%',method:'BP 2023 – UV'},
{id:6,monographId:2,seq:2,name:'Dissolution',spec:'NLT 75% in 30 min',method:'USP <711>'},
{id:7,monographId:2,seq:3,name:'Hardness',spec:'4 – 8 kP',method:'In-house SOP-QC-010'},
{id:8,monographId:2,seq:4,name:'Friability',spec:'NMT 1.0%',method:'USP <1216>'},
],

batches:[
{id:1,productId:1,batchNo:'AMX-2024-001',mfgDate:'2024-01-10',incubationDate:'01 Mar 2024',expiry:'05 Mar 2024',studyType:'Long Study',shelf:'S1',rack:'R2',position:'P1',qtyPlaced:60,qtyRemaining:60,status:'Active'},
{id:2,productId:2,batchNo:'PCM-2024-001',mfgDate:'2024-03-01',incubationDate:'01 Mar 2024',expiry:'05 Mar 2024',studyType:'Accelerated Study',shelf:'S1',rack:'R2',position:'P1',qtyPlaced:45,qtyRemaining:30,status:'Active'},
{id:3,productId:1,batchNo:'AMX-2024-002',mfgDate:'2024-05-20',incubationDate:'2024-06-01',expiry:'2027-06-01',studyType:'Long Study',shelf:'S2',rack:'R1',position:'P2',qtyPlaced:60,qtyRemaining:45,status:'Active'},
{id:4,productId:3,batchNo:'OMP-2024-001',mfgDate:'2024-02-01',incubationDate:'01 Feb 2024',expiry:'10 Feb 2024',studyType:'Accelerated Study',shelf:'S2',rack:'R2',position:'P1',qtyPlaced:30,qtyRemaining:10,status:'Active'},
{id:5,productId:2,batchNo:'PCM-2024-002',mfgDate:'2024-02-15',incubationDate:'01 Mar 2024',expiry:'05 Mar 2024',studyType:'Accelerated Study',shelf:'S1',rack:'R2',position:'P1',qtyPlaced:45,qtyRemaining:45,status:'Active'},
],

testPoints:[],

results:{},

pulls:{},

locationHistory:[],

nextId:{
product:10,
monograph:10,
test:20,
batch:10,
testPoint:100
}

}