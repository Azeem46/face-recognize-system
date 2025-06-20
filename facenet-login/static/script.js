const video = document.getElementById('video');
navigator.mediaDevices.getUserMedia({video:true}).then(s=>video.srcObject=s);

function capture(mode){
  const canvas=document.createElement('canvas');
  canvas.width=640; canvas.height=480;
  canvas.getContext('2d').drawImage(video,0,0,640,480);
  canvas.toBlob(blob=>{
    const form = new FormData();
    form.append('image',blob);
    if(mode==='register') form.append('name',document.getElementById('name').value);
    fetch(`/${mode}`,{method:'POST',body:form})
      .then(r=>r.json()).then(j=>{
        if (mode === 'login' && j.status === 'ok') {
            window.location.href = '/welcome';
        } else {
            alert(JSON.stringify(j));
        }
      });
  },'image/jpeg');
}
