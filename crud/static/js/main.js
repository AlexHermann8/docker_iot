
const btnDelete = document.querySelectorAll('.btn-borrar');

if (btnDelete.length > 0) { 
  const btnArray = Array.from(btnDelete);
  btnArray.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      if(!confirm('¿Está seguro de querer borrar?')){
        e.preventDefault();
      }
    });
  });
}

document.addEventListener('DOMContentLoaded', () => {
    const themeStylesheet = document.getElementById('theme-stylesheet');
    const themeSelector = document.getElementById('themeSelector');
    const themes = {
        light: 'https://bootswatch.com/5/cosmo/bootstrap.min.css',
        dark: 'https://bootswatch.com/5/darkly/bootstrap.min.css'
    };
    const savedTheme = localStorage.getItem('selectedTheme') || 'light';
    if (themeStylesheet) {
        themeStylesheet.setAttribute('href', themes[savedTheme]);
    }
    if (themeSelector) {
        themeSelector.value = savedTheme;
        themeSelector.addEventListener('change', (event) => {
            const newTheme = event.target.value;
            if (themeStylesheet) {
                themeStylesheet.setAttribute('href', themes[newTheme]);
            }
            localStorage.setItem('selectedTheme', newTheme);
        });
    }
});