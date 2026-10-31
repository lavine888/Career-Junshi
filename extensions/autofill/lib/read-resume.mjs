import {makeProfile,sha256} from './core.mjs';

export async function readResume(file,{ocr=false,progress=()=>{}}={}) {
  if(!file||file.size>12*1024*1024)throw Error('请选择不超过12MB的简历文件。');
  const bytes=new Uint8Array(await file.arrayBuffer());
  const sha=await sha256(bytes);
  let text='',structured=null,ocrUsed=false;
  if(file.type.startsWith('image/')||/\.(png|jpe?g|webp|bmp)$/i.test(file.name)) {
    if(!ocr)throw Error('图片简历请勾选“使用本地OCR”，识别后检查文字。');
    text=await recognize(file,progress);ocrUsed=true;
  } else if(String.fromCharCode(...bytes.slice(0,5))==='%PDF-') {
    progress('正在本地提取PDF文字…');
    const pdfjs=await import('../vendor/pdf/pdf.mjs');
    pdfjs.GlobalWorkerOptions.workerSrc=chrome.runtime.getURL('vendor/pdf/pdf.worker.mjs');
    const loadingTask=pdfjs.getDocument({data:bytes.slice(),isEvalSupported:false,useSystemFonts:true});
    try {
      const pdf=await loadingTask.promise;
      if(pdf.numPages>12)throw Error('请使用12页以内的简历。');
      for(let i=1;i<=pdf.numPages;i++){
        const page=await pdf.getPage(i),items=(await page.getTextContent()).items;
        let pageText='';
        for(const item of items)pageText+=item.str+(item.hasEOL?'\n':' ');
        if(pageText.trim().length<20&&ocr){
          const viewport=page.getViewport({scale:2}),canvas=document.createElement('canvas');
          canvas.width=viewport.width;canvas.height=viewport.height;
          await page.render({canvasContext:canvas.getContext('2d'),viewport}).promise;
          pageText=await recognize(canvas,progress);ocrUsed=true;
        }
        text+=pageText+'\n';
      }
    }finally{await loadingTask.destroy();}
    if(text.trim().length<20)throw Error('PDF没有可用文字层；请勾选本地OCR重新导入。');
  } else {
    try{text=new TextDecoder('utf-8',{fatal:true}).decode(bytes);}catch{throw Error('请用UTF-8文字、JSON、PDF或图片简历。');}
    if(/\.json$/i.test(file.name)) {
      structured=JSON.parse(text);
      if(structured.schema_version!=='1'||!Array.isArray(structured.sections))throw Error('JSON需要是军师简历导出的resume-data.json格式。');
      // Drop source maps and any unrelated metadata from the filling context.
      text=[structured.name,...(structured.contacts||[]),...structured.sections.flatMap(s=>(s.entries||[]).flatMap(e=>[e.title,e.subtitle,e.dates,...(e.bullets||[]).filter(b=>b.confidence!=='PLANNED').map(b=>b.text)]))].filter(Boolean).join('\n');
    }
  }
  return makeProfile(text,{name:file.name,sha,structured,ocr:ocrUsed});
}

async function recognize(image,progress){
  if(!globalThis.Tesseract)throw Error('本地OCR组件缺失，请按安装说明准备vendor文件。');
  progress('正在启动本地中英文OCR…');
  const base=chrome.runtime.getURL('vendor/ocr/');
  const worker=await Tesseract.createWorker('chi_sim+eng',1,{
    workerPath:base+'worker.min.js',corePath:base+'core',langPath:base+'lang',workerBlobURL:false,
    logger:m=>{if(m.status==='recognizing text')progress(`OCR识别中 ${Math.round(m.progress*100)}%`);}
  });
  try{const result=await worker.recognize(image);progress(`OCR完成，需检查文字（引擎置信度 ${Math.round(result.data.confidence)}）`);return result.data.text;}
  finally{await worker.terminate();}
}
