async function shorten(){
    let url=document.getElementById("url").value;

    let res=await fetch('/api/shorten?url='+url,{method:'POST'});
    let data=await res.json();

    document.getElementById("result").innerHTML =
    `<a href="${data.short_url}" target="_blank">${data.short_url}</a>`;

}
