const btn = document.querySelector('.btn');
const selectmenu1 = document.querySelector('.selectmenu1');
const selectmenu2 = document.querySelector('.selectmenu2');
const selectmenu3 = document.querySelector('.selectmenu3');
const selectmenu4 = document.querySelector('.selectmenu4');
const selectmenu5 = document.querySelector('.selectmenu5');
const selectmenu6 = document.querySelector('.selectmenu6');

btn.addEventListener('click',()=>{
    btn.style.backgroundColor = '#E22EFF';
    btn.style.transition='.5s ease';
})
selectmenu1.addEventListener('click',()=>{
    selectmenu1.style.backgroundColor = '#FFDC2E';
    selectmenu1.style.transition='.5s ease';
    selectmenu2.style.backgroundColor = '#ffffff';
    selectmenu3.style.backgroundColor = '#ffffff';
    selectmenu4.style.backgroundColor = '#ffffff';
    selectmenu5.style.backgroundColor = '#ffffff';
    selectmenu6.style.backgroundColor = '#ffffff';
})
selectmenu2.addEventListener('click',()=>{
    selectmenu2.style.backgroundColor = '#FFDC2E';
    selectmenu2.style.transition='.5s ease';
    selectmenu1.style.backgroundColor = '#ffffff';
    selectmenu3.style.backgroundColor = '#ffffff';
    selectmenu4.style.backgroundColor = '#ffffff';
    selectmenu5.style.backgroundColor = '#ffffff';
    selectmenu6.style.backgroundColor = '#ffffff';
})
selectmenu3.addEventListener('click',()=>{
    selectmenu3.style.backgroundColor = '#FFDC2E';
    selectmenu3.style.transition='.5s ease';
    selectmenu2.style.backgroundColor = '#ffffff';
    selectmenu1.style.backgroundColor = '#ffffff';
    selectmenu4.style.backgroundColor = '#ffffff';
    selectmenu5.style.backgroundColor = '#ffffff';
    selectmenu6.style.backgroundColor = '#ffffff';
})
selectmenu4.addEventListener('click',()=>{
    selectmenu4.style.backgroundColor = '#FFDC2E';
    selectmenu4.style.transition='.5s ease';
    selectmenu2.style.backgroundColor = '#ffffff';
    selectmenu3.style.backgroundColor = '#ffffff';
    selectmenu1.style.backgroundColor = '#ffffff';
    selectmenu5.style.backgroundColor = '#ffffff';
    selectmenu6.style.backgroundColor = '#ffffff';
})
selectmenu5.addEventListener('click',()=>{
    selectmenu5.style.backgroundColor = '#FFDC2E';
    selectmenu5.style.transition='.5s ease';
    selectmenu2.style.backgroundColor = '#ffffff';
    selectmenu3.style.backgroundColor = '#ffffff';
    selectmenu4.style.backgroundColor = '#ffffff';
    selectmenu1.style.backgroundColor = '#ffffff';
    selectmenu6.style.backgroundColor = '#ffffff';
})
selectmenu6.addEventListener('click',()=>{
    selectmenu6.style.backgroundColor = '#FFDC2E';
    selectmenu6.style.transition='.5s ease';
    selectmenu2.style.backgroundColor = '#ffffff';
    selectmenu3.style.backgroundColor = '#ffffff';
    selectmenu4.style.backgroundColor = '#ffffff';
    selectmenu5.style.backgroundColor = '#ffffff';
    selectmenu1.style.backgroundColor = '#ffffff';
})