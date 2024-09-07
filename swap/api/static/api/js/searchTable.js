function searchTable (tableId, value) {
    const filter = value.toLowerCase();
    const table = document.getElementById(tableId);
    const rows = table.getElementsByTagName('tr');
    
    // If the input value is less than 3 characters, show all rows and return
    if (filter.length < 3) {
      for (let i = 1; i < rows.length; i++) {
        rows[i].style.display = '';
      }
      return;
    }
  
    const filterLength = filter.length;
    
    for (let i = 1; i < rows.length; i++) { // skip first row as this is the header row
      const row = rows[i];
      let textContent = row.textContent.toLowerCase(); // Get all text content at once
  
      if (textContent.indexOf(filter) > -1) {
        row.style.display = '';
      } else {
        row.style.display = 'none';
      }
    }
  }
  
  function addSearchListeners (inputs) {
    inputs.forEach(input => {
      input.addEventListener('input', (event) => {
        const target = event.target;
        const targetTableId = target.dataset.tableId;
        const value = target.value;
        searchTable(targetTableId, value);
      });
    });
  }
  
  const searchInputs = Array.from(document.getElementsByClassName('searchInput'));
  
  addSearchListeners(searchInputs);