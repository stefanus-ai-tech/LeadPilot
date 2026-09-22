const $ = (id) => document.getElementById(id);
const form = $('lead-form');
let busy = false, lastResult = null;
const samples = {
  hot: {name:'Sarah Miller',email:'sarah@example.com',company:'Acme Labs',company_size:45,budget:5000000,timeline:'Minggu depan',message:'Kami ingin membeli jasa automation untuk sales. Tolong integrasikan form website ke Google Sheets dan kirim notifikasi lead. Kami mau mulai minggu depan.'},
  research: {name:'Raka Putra',email:'raka@example.com',company:'Studio Raka',company_size:8,budget:'',timeline:'Belum ada target',message:'Saya sedang riset pilihan automation untuk bisnis kecil. Boleh tahu contoh penggunaan dan kisaran biayanya? Belum ada rencana membeli atau mulai dalam waktu dekat.'},
  support: {name:'Dina Putri',email:'dina@example.com',company:'Kopi Senja',company_size:'',budget:'',timeline:'Hari ini',message:'Saya pelanggan yang sudah menggunakan integrasi Google Sheets. Sejak pagi data form tidak masuk. Tolong bantu cek error pada workflow yang sudah berjalan.'}
};
function count(){ $('char-count').textContent=`${form.elements.message.value.length} / 8000`; }
function clearResult(){lastResult=null;$('result').hidden=true;$('loading').hidden=true;$('empty').hidden=false;$('error').hidden=true;}
document.querySelectorAll('[data-sample]').forEach(button=>button.addEventListener('click',()=>{
  if(busy)return;form.reset();Object.entries(samples[button.dataset.sample]).forEach(([k,v])=>form.elements[k].value=v);count();clearResult();
}));
form.elements.message.addEventListener('input',count);
form.addEventListener('input',()=>{if(!busy)clearResult();});
form.addEventListener('reset',()=>{if(!busy){clearResult();setTimeout(count,0);}});
$('portrait').addEventListener('click',()=>{const enabled=document.body.classList.toggle('portrait');$('portrait').setAttribute('aria-pressed',String(enabled));$('portrait').textContent=enabled?'▤ Mode desktop':'▯ Mode short';});
function text(id,value){$(id).textContent=value;}
function render(result,seconds){
  const {analysis:a,scoring:s,lead:l}=result;
  $('output').style.setProperty('--accent',s.tier==='HOT'?'#c3f58b':s.tier==='WARM'?'#f5ce83':'#a0c9ed');
  text('result-name',l.name+(l.company?' / '+l.company:''));
  text('result-title',a.intent==='support'?'Bantu pelanggan ini.':a.intent==='spam'?'Saring sebelum lanjut.':s.tier==='HOT'?'Peluang yang menjanjikan.':s.tier==='WARM'?'Layak diajak ngobrol.':'Kenali kebutuhannya dulu.');
  text('tier',`${s.tier} LEAD`);text('score',s.score);$('score-circle').style.setProperty('--score',s.score);
  text('intent',({purchase:'Siap membeli',research:'Riset',support:'Support',spam:'Spam',unknown:'Belum jelas'})[a.intent]);
  text('urgency',({high:'Tinggi',medium:'Sedang',low:'Rendah',unknown:'Belum jelas'})[a.urgency]);
  text('fit',a.service_match?'Cocok':'Belum cocok');text('summary',a.summary);
  $('reasons').replaceChildren();
  const labels={'Budget >= Rp5.000.000':'Budget ≥ Rp5 juta','Budget >= Rp2.000.000':'Budget ≥ Rp2 juta','Budget provided':'Budget tersedia','Company size 20-200':'Perusahaan 20–200 karyawan','Company size >= 5':'Perusahaan ≥ 5 karyawan','Service matches our offering':'Layanan sesuai kebutuhan','High urgency':'Urgensi tinggi','Medium urgency':'Urgensi sedang','Strong purchase intent':'Niat membeli kuat'};
  for(const reason of s.reasons){const li=document.createElement('li'),label=document.createElement('span'),points=document.createElement('b');const match=reason.match(/^(.*?) \(\+(\d+)\)$/);label.textContent=match?(labels[match[1]]||match[1]):reason;points.textContent=match?`+${match[2]}`:'';li.append(label,points);$('reasons').append(li);}
  if(!s.reasons.length){const li=document.createElement('li');li.textContent='Belum ada sinyal yang menambah skor.';$('reasons').append(li);}
  text('next',a.intent==='support'?'Arahkan ke bantuan pelanggan dan cek kendala yang dilaporkan.':a.intent==='spam'?'Tinjau relevansi pesan sebelum melakukan follow-up.':s.requires_human_review?'Baca ulang pesan dan konfirmasi kebutuhan sebelum menindaklanjuti.':s.tier==='HOT'?'Hubungi calon klien dan jadwalkan diskusi kebutuhan.':s.tier==='WARM'?'Kirim contoh solusi, lalu konfirmasi budget dan timeline.':'Kirim informasi awal dan gali kebutuhan lebih lanjut.');
  $('review').hidden=!s.requires_human_review;text('duration',`Laya · ${seconds}s · Diproses lokal`);
  $('loading').hidden=true;$('result').hidden=false;
}
form.addEventListener('submit',async(event)=>{
  event.preventDefault();if(busy)return;
  const payload=Object.fromEntries(new FormData(form));
  for(const key of ['budget','company_size']){payload[key]=payload[key]===''?null:Number(payload[key]);if(payload[key]!==null&&!Number.isSafeInteger(payload[key])){text('error','Budget dan jumlah karyawan harus berupa bilangan bulat yang valid.');$('error').hidden=false;return;}}
  payload.source='LeadPilot demo';busy=true;clearResult();$('empty').hidden=true;$('loading').hidden=false;$('output').setAttribute('aria-busy','true');
  const controls=[...form.elements,...document.querySelectorAll('[data-sample]')];controls.forEach(el=>el.disabled=true);text('elapsed','0s');
  const start=performance.now(),timer=setInterval(()=>text('elapsed',`${Math.floor((performance.now()-start)/1000)}s`),1000);
  const controller=new AbortController(),timeout=setTimeout(()=>controller.abort(),180000);
  try{
    const response=await fetch('/triage',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload),signal:controller.signal});
    const result=await response.json();
    if(!response.ok){const messages={422:'Cek kembali data lead. Nama, email, dan pesan minimal 5 karakter wajib diisi.',502:'Output AI belum valid. Coba analisis sekali lagi.',503:'Laya belum siap. Pastikan paket dan checkpoint Laya tersedia.',504:'Analisis terlalu lama. Coba lagi setelah model selesai dimuat.'};throw new Error(messages[response.status]||'Analisis gagal. Coba lagi.');}
    lastResult=result;render(result,((performance.now()-start)/1000).toFixed(1));
    if(document.body.classList.contains('portrait')||innerWidth<721)$('output').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'start'});
  }catch(error){$('loading').hidden=true;$('empty').hidden=false;text('error',error.name==='AbortError'?'Waktu tunggu habis. Coba lagi setelah Laya siap.':error instanceof TypeError?'Koneksi ke LeadPilot terputus. Pastikan server masih berjalan.':error.message);$('error').hidden=false;}
  finally{clearInterval(timer);clearTimeout(timeout);busy=false;controls.forEach(el=>el.disabled=false);$('output').setAttribute('aria-busy','false');}
});
$('download').addEventListener('click',()=>{if(!lastResult)return;const url=URL.createObjectURL(new Blob([JSON.stringify(lastResult,null,2)],{type:'application/json'}));const link=document.createElement('a');link.href=url;link.download='leadpilot-result.json';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
