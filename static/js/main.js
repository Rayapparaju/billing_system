document.addEventListener('DOMContentLoaded', function() {

  // Sidebar toggle
  const toggleBtn = document.querySelector('.sidebar-toggle');
  const sidebar = document.querySelector('.sidebar');
  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', function() {
      sidebar.classList.toggle('open');
    });
    document.addEventListener('click', function(e) {
      if (window.innerWidth <= 992) {
        if (!sidebar.contains(e.target) && !toggleBtn.contains(e.target)) {
          sidebar.classList.remove('open');
        }
      }
    });
  }

  // Auto-dismiss messages
  const alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach(function(alert) {
    setTimeout(function() {
      alert.style.transition = 'opacity 0.3s';
      alert.style.opacity = '0';
      setTimeout(function() {
        alert.remove();
      }, 300);
    }, 4000);
  });

  // Delete confirmation modals
  document.querySelectorAll('[data-delete-url]').forEach(function(btn) {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const url = btn.getAttribute('data-delete-url');
      const item = btn.getAttribute('data-item') || 'this item';
      const modal = document.getElementById('deleteModal');
      if (modal) {
        document.getElementById('deleteItemName').textContent = item;
        document.getElementById('confirmDeleteBtn').setAttribute('href', url);
        modal.classList.add('active');
      }
    });
  });

  // Close modal
  document.querySelectorAll('.modal-overlay').forEach(function(modal) {
    modal.addEventListener('click', function(e) {
      if (e.target === modal) {
        modal.classList.remove('active');
      }
    });
  });

  // Close modal with close buttons
  document.querySelectorAll('[data-close-modal]').forEach(function(btn) {
    btn.addEventListener('click', function() {
      btn.closest('.modal-overlay').classList.remove('active');
    });
  });

  // Invoice items management
  const itemsContainer = document.getElementById('itemsContainer');
  const addItemBtn = document.getElementById('addItemBtn');

  function getProductById(id) {
    return productList.find(function(p) { return p.id === id; });
  }

  function updateRowTotal(row) {
    const qty = parseFloat(row.querySelector('.item-qty').value) || 0;
    const rate = parseFloat(row.querySelector('.item-rate').value) || 0;
    const gstPct = parseFloat(row.querySelector('.item-gst').value) || 0;
    const discPct = parseFloat(row.querySelector('.item-discount').value) || 0;
    const itemTotal = qty * rate;
    const gstAmt = itemTotal * (gstPct / 100);
    const discAmt = discPct > 0 ? itemTotal * (discPct / 100) : 0;
    const lineTotal = itemTotal + gstAmt - discAmt;
    row.querySelector('.item-total').value = lineTotal.toFixed(2);
    row.querySelector('.item-total-display').textContent = lineTotal.toFixed(2);
    calculateInvoiceTotals();
  }

  function calculateInvoiceTotals() {
    let subtotal = 0;
    let totalGst = 0;
    let totalDiscount = 0;
    document.querySelectorAll('.item-row:not(.header-row)').forEach(function(row) {
      const qty = parseFloat(row.querySelector('.item-qty').value) || 0;
      const rate = parseFloat(row.querySelector('.item-rate').value) || 0;
      const gstPct = parseFloat(row.querySelector('.item-gst').value) || 0;
      const discPct = parseFloat(row.querySelector('.item-discount').value) || 0;
      const itemTotal = qty * rate;
      const gstAmt = itemTotal * (gstPct / 100);
      const discAmt = discPct > 0 ? itemTotal * (discPct / 100) : 0;
      subtotal += itemTotal;
      totalGst += gstAmt;
      totalDiscount += discAmt;
    });
    const grandTotal = subtotal + totalGst - totalDiscount;
    const subEl = document.getElementById('calcSubtotal');
    const gstEl = document.getElementById('calcGst');
    const discEl = document.getElementById('calcDiscount');
    const grandEl = document.getElementById('calcGrandTotal');
    if (subEl) subEl.textContent = subtotal.toFixed(2);
    if (gstEl) gstEl.textContent = totalGst.toFixed(2);
    if (discEl) discEl.textContent = totalDiscount.toFixed(2);
    if (grandEl) grandEl.textContent = grandTotal.toFixed(2);
  }

  if (addItemBtn && itemsContainer) {
    addItemBtn.addEventListener('click', function() {
      const row = document.createElement('div');
      row.className = 'item-row fade-in';
      row.innerHTML = `
        <select class="form-control item-product" required>
          <option value="">-- Select Product --</option>
          ${productList.map(function(p) {
            return '<option value="' + p.id + '" data-price="' + p.price + '" data-gst="' + p.gst + '">' + p.name + '</option>';
          }).join('')}
        </select>
        <input type="number" class="form-control item-qty" value="1" min="1" required>
        <input type="number" class="form-control item-rate" step="0.01" min="0" required>
        <input type="number" class="form-control item-gst" step="0.01" value="0" min="0">
        <input type="number" class="form-control item-discount" step="0.01" value="0" min="0">
        <span class="item-total-display" style="font-weight:600;">0.00</span>
        <input type="hidden" class="item-total" value="0">
        <button type="button" class="remove-btn" title="Remove"><i class="fas fa-times"></i></button>
      `;
      itemsContainer.appendChild(row);
      row.querySelector('.item-product').addEventListener('change', function() {
        const selected = this.options[this.selectedIndex];
        const price = selected.getAttribute('data-price') || 0;
        const gst = selected.getAttribute('data-gst') || 0;
        row.querySelector('.item-rate').value = price;
        row.querySelector('.item-gst').value = gst;
        updateRowTotal(row);
      });
      row.querySelectorAll('.item-qty, .item-rate, .item-gst, .item-discount').forEach(function(inp) {
        inp.addEventListener('input', function() { updateRowTotal(row); });
      });
      row.querySelector('.remove-btn').addEventListener('click', function() {
        row.remove();
        calculateInvoiceTotals();
      });
      updateRowTotal(row);
    });
  }

  // Collect items data on form submit
  const invoiceForm = document.querySelector('.invoice-form');
  if (invoiceForm) {
    invoiceForm.addEventListener('submit', function(e) {
      const items = [];
      document.querySelectorAll('.item-row:not(.header-row)').forEach(function(row) {
        const productId = row.querySelector('.item-product').value;
        if (productId) {
          items.push({
            product_id: productId,
            quantity: row.querySelector('.item-qty').value,
            rate: row.querySelector('.item-rate').value,
            gst: row.querySelector('.item-gst').value || 0,
            discount: row.querySelector('.item-discount').value || 0,
          });
        }
      });
      if (items.length === 0) {
        e.preventDefault();
        alert('Please add at least one item.');
        return;
      }
      document.getElementById('id_items').value = JSON.stringify(items);
    });
  }

});
