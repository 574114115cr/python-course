/* 单元课件播放器的附加能力：全屏 + 记住上次看到第几页。
   独立文件是为了让 build_all_lesson_ppt.py 重建播放器时不会再丢（内联脚本
   塞进 f-string 模板会撞花括号）。依赖页面里的全局变量 U / S / cur / show。 */
(function(){
  var fs=document.getElementById('fsBtn');
  if(fs){
    fs.addEventListener('click', function(e){
      e.preventDefault();
      var el=document.querySelector('.stage');
      if(document.fullscreenElement){ document.exitFullscreen(); }
      else if(el && el.requestFullscreen){ el.requestFullscreen(); }
    });
  }
  var KEY='ppt-u'+U+'-page';
  var _show=show;
  show=function(i,push){
    _show(i,push);
    if(push!==false){ try{ localStorage.setItem(KEY,String(cur)); }catch(e){} }
  };
  if(!/^#s\d+$/.test(location.hash||'')){
    var last=parseInt(localStorage.getItem(KEY)||'0',10);
    if(last>0 && last<S.length) _show(last,false);
  }
})();
