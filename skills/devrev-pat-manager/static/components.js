/**
 * Twenty Design System - Component Behaviors
 * JavaScript interactions for UI components
 */

// ========================================
// DROPDOWN / MENU
// ========================================

class Dropdown {
  constructor(trigger, menu, options = {}) {
    this.trigger = trigger;
    this.menu = menu;
    this.options = {
      closeOnSelect: true,
      closeOnOutsideClick: true,
      placement: 'bottom-start',
      ...options
    };
    this.isOpen = false;
    this.init();
  }

  init() {
    this.trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      this.toggle();
    });

    if (this.options.closeOnOutsideClick) {
      document.addEventListener('click', (e) => {
        if (this.isOpen && !this.menu.contains(e.target)) {
          this.close();
        }
      });
    }

    if (this.options.closeOnSelect) {
      this.menu.querySelectorAll('.menu-item').forEach(item => {
        item.addEventListener('click', () => this.close());
      });
    }

    // Close on Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isOpen) {
        this.close();
      }
    });
  }

  toggle() {
    this.isOpen ? this.close() : this.open();
  }

  open() {
    this.menu.style.display = 'block';
    this.isOpen = true;
    this.trigger.setAttribute('aria-expanded', 'true');
  }

  close() {
    this.menu.style.display = 'none';
    this.isOpen = false;
    this.trigger.setAttribute('aria-expanded', 'false');
  }
}

// ========================================
// MODAL
// ========================================

class Modal {
  constructor(modal, options = {}) {
    this.modal = modal;
    this.options = {
      closeOnBackdrop: true,
      closeOnEscape: true,
      ...options
    };
    this.isOpen = false;
    this.init();
  }

  init() {
    // Close button
    const closeBtn = this.modal.querySelector('[data-modal-close]');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => this.close());
    }

    // Backdrop click
    if (this.options.closeOnBackdrop) {
      this.modal.addEventListener('click', (e) => {
        if (e.target === this.modal) {
          this.close();
        }
      });
    }

    // Escape key
    if (this.options.closeOnEscape) {
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && this.isOpen) {
          this.close();
        }
      });
    }
  }

  open() {
    this.modal.style.display = 'flex';
    this.isOpen = true;
    document.body.style.overflow = 'hidden';
    this.modal.setAttribute('aria-hidden', 'false');
  }

  close() {
    this.modal.style.display = 'none';
    this.isOpen = false;
    document.body.style.overflow = '';
    this.modal.setAttribute('aria-hidden', 'true');
  }
}

// ========================================
// TABS
// ========================================

class Tabs {
  constructor(container, options = {}) {
    this.container = container;
    this.tabs = container.querySelectorAll('.tab');
    this.panels = container.querySelectorAll('.tab-panel');
    this.options = {
      onChange: null,
      ...options
    };
    this.init();
  }

  init() {
    this.tabs.forEach((tab, index) => {
      tab.addEventListener('click', () => this.activate(index));
    });
  }

  activate(index) {
    // Update tabs
    this.tabs.forEach((tab, i) => {
      tab.classList.toggle('active', i === index);
      tab.setAttribute('aria-selected', i === index);
    });

    // Update panels
    this.panels.forEach((panel, i) => {
      panel.style.display = i === index ? 'block' : 'none';
    });

    if (this.options.onChange) {
      this.options.onChange(index);
    }
  }
}

// ========================================
// TOGGLE / SWITCH
// ========================================

class Toggle {
  constructor(input, options = {}) {
    this.input = input;
    this.options = {
      onChange: null,
      ...options
    };
    this.init();
  }

  init() {
    this.input.addEventListener('change', () => {
      if (this.options.onChange) {
        this.options.onChange(this.input.checked);
      }
    });
  }

  toggle() {
    this.input.checked = !this.input.checked;
    this.input.dispatchEvent(new Event('change'));
  }

  on() {
    this.input.checked = true;
    this.input.dispatchEvent(new Event('change'));
  }

  off() {
    this.input.checked = false;
    this.input.dispatchEvent(new Event('change'));
  }
}

// ========================================
// TOOLTIP
// ========================================

class Tooltip {
  constructor(trigger, content, options = {}) {
    this.trigger = trigger;
    this.content = content;
    this.options = {
      placement: 'top',
      delay: 200,
      ...options
    };
    this.tooltip = null;
    this.timeout = null;
    this.init();
  }

  init() {
    this.trigger.addEventListener('mouseenter', () => this.show());
    this.trigger.addEventListener('mouseleave', () => this.hide());
    this.trigger.addEventListener('focus', () => this.show());
    this.trigger.addEventListener('blur', () => this.hide());
  }

  show() {
    this.timeout = setTimeout(() => {
      this.tooltip = document.createElement('div');
      this.tooltip.className = 'tooltip';
      this.tooltip.textContent = this.content;
      document.body.appendChild(this.tooltip);
      this.position();
    }, this.options.delay);
  }

  hide() {
    clearTimeout(this.timeout);
    if (this.tooltip) {
      this.tooltip.remove();
      this.tooltip = null;
    }
  }

  position() {
    if (!this.tooltip) return;

    const triggerRect = this.trigger.getBoundingClientRect();
    const tooltipRect = this.tooltip.getBoundingClientRect();
    const gap = 8;

    let top, left;

    switch (this.options.placement) {
      case 'top':
        top = triggerRect.top - tooltipRect.height - gap;
        left = triggerRect.left + (triggerRect.width - tooltipRect.width) / 2;
        break;
      case 'bottom':
        top = triggerRect.bottom + gap;
        left = triggerRect.left + (triggerRect.width - tooltipRect.width) / 2;
        break;
      case 'left':
        top = triggerRect.top + (triggerRect.height - tooltipRect.height) / 2;
        left = triggerRect.left - tooltipRect.width - gap;
        break;
      case 'right':
        top = triggerRect.top + (triggerRect.height - tooltipRect.height) / 2;
        left = triggerRect.right + gap;
        break;
    }

    this.tooltip.style.position = 'fixed';
    this.tooltip.style.top = `${top}px`;
    this.tooltip.style.left = `${left}px`;
  }
}

// ========================================
// TOAST / NOTIFICATION
// ========================================

class Toast {
  static container = null;
  static queue = [];

  static init() {
    if (!Toast.container) {
      Toast.container = document.createElement('div');
      Toast.container.className = 'toast-container';
      Toast.container.style.cssText = `
        position: fixed;
        bottom: 24px;
        right: 24px;
        display: flex;
        flex-direction: column;
        gap: 8px;
        z-index: 800;
      `;
      document.body.appendChild(Toast.container);
    }
  }

  static show(message, options = {}) {
    Toast.init();

    const defaults = {
      type: 'info', // info, success, warning, error
      duration: 4000,
      dismissible: true
    };

    const config = { ...defaults, ...options };

    const toast = document.createElement('div');
    toast.className = `banner banner-${config.type}`;
    toast.style.cssText = `
      min-width: 300px;
      animation: slideIn 0.2s ease;
    `;

    // Build DOM safely without innerHTML for user content
    const content = document.createElement('div');
    content.className = 'banner-content';

    const title = document.createElement('div');
    title.className = 'banner-title';
    title.textContent = message; // Use textContent to prevent XSS
    content.appendChild(title);

    toast.appendChild(content);

    if (config.dismissible) {
      const closeBtn = document.createElement('button');
      closeBtn.className = 'btn btn-ghost btn-icon banner-close';
      closeBtn.setAttribute('aria-label', 'Close');
      closeBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M4 4L12 12M12 4L4 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>';
      closeBtn.addEventListener('click', () => {
        Toast.dismiss(toast);
      });
      toast.appendChild(closeBtn);
    }

    Toast.container.appendChild(toast);

    if (config.duration > 0) {
      setTimeout(() => Toast.dismiss(toast), config.duration);
    }

    return toast;
  }

  static dismiss(toast) {
    toast.style.animation = 'slideOut 0.2s ease forwards';
    setTimeout(() => toast.remove(), 200);
  }

  static success(message, options = {}) {
    return Toast.show(message, { ...options, type: 'success' });
  }

  static error(message, options = {}) {
    return Toast.show(message, { ...options, type: 'error' });
  }

  static warning(message, options = {}) {
    return Toast.show(message, { ...options, type: 'warning' });
  }

  static info(message, options = {}) {
    return Toast.show(message, { ...options, type: 'info' });
  }
}

// Add toast animations
const style = document.createElement('style');
style.textContent = `
  @keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }
  @keyframes slideOut {
    from { transform: translateX(0); opacity: 1; }
    to { transform: translateX(100%); opacity: 0; }
  }
`;
document.head.appendChild(style);

// ========================================
// ACCORDION
// ========================================

class Accordion {
  constructor(container, options = {}) {
    this.container = container;
    this.items = container.querySelectorAll('.accordion-item');
    this.options = {
      allowMultiple: false,
      ...options
    };
    this.init();
  }

  init() {
    this.items.forEach(item => {
      const header = item.querySelector('.accordion-header');
      const content = item.querySelector('.accordion-content');

      header.addEventListener('click', () => {
        const isOpen = item.classList.contains('open');

        if (!this.options.allowMultiple) {
          this.items.forEach(i => {
            i.classList.remove('open');
            i.querySelector('.accordion-content').style.maxHeight = null;
          });
        }

        if (!isOpen) {
          item.classList.add('open');
          content.style.maxHeight = content.scrollHeight + 'px';
        } else {
          item.classList.remove('open');
          content.style.maxHeight = null;
        }
      });
    });
  }
}

// ========================================
// RATING
// ========================================

class Rating {
  constructor(container, options = {}) {
    this.container = container;
    this.options = {
      maxRating: 5,
      value: 0,
      onChange: null,
      readOnly: false,
      ...options
    };
    this.value = this.options.value;
    this.init();
  }

  init() {
    this.container.innerHTML = '';
    this.container.classList.add('rating');

    for (let i = 1; i <= this.options.maxRating; i++) {
      const star = document.createElement('span');
      star.className = 'rating-star';
      star.innerHTML = '<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M8 1l2.245 4.549 5.021.73-3.633 3.541.858 5.002L8 12.347l-4.491 2.475.858-5.002L.734 6.279l5.021-.73L8 1z"/></svg>';

      if (i <= this.value) {
        star.classList.add('filled');
      }

      if (!this.options.readOnly) {
        star.addEventListener('click', () => this.setValue(i));
        star.addEventListener('mouseenter', () => this.highlight(i));
        star.addEventListener('mouseleave', () => this.highlight(this.value));
      }

      this.container.appendChild(star);
    }
  }

  setValue(value) {
    this.value = value;
    this.highlight(value);
    if (this.options.onChange) {
      this.options.onChange(value);
    }
  }

  highlight(value) {
    const stars = this.container.querySelectorAll('.rating-star');
    stars.forEach((star, i) => {
      star.classList.toggle('filled', i < value);
    });
  }
}

// ========================================
// SEARCH INPUT
// ========================================

class SearchInput {
  constructor(input, options = {}) {
    this.input = input;
    this.options = {
      onSearch: null,
      debounce: 300,
      minLength: 2,
      ...options
    };
    this.timeout = null;
    this.init();
  }

  init() {
    this.input.addEventListener('input', () => {
      clearTimeout(this.timeout);

      if (this.input.value.length >= this.options.minLength) {
        this.timeout = setTimeout(() => {
          if (this.options.onSearch) {
            this.options.onSearch(this.input.value);
          }
        }, this.options.debounce);
      }
    });

    // Clear on Escape
    this.input.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        this.clear();
      }
    });
  }

  clear() {
    this.input.value = '';
    if (this.options.onSearch) {
      this.options.onSearch('');
    }
  }
}

// ========================================
// COPY TO CLIPBOARD
// ========================================

async function copyToClipboard(text, options = {}) {
  const defaults = {
    showToast: true,
    successMessage: 'Copied to clipboard',
    errorMessage: 'Failed to copy'
  };

  const config = { ...defaults, ...options };

  try {
    await navigator.clipboard.writeText(text);
    if (config.showToast) {
      Toast.success(config.successMessage);
    }
    return true;
  } catch (err) {
    if (config.showToast) {
      Toast.error(config.errorMessage);
    }
    return false;
  }
}

// ========================================
// THEME TOGGLE
// ========================================

class ThemeToggle {
  constructor(options = {}) {
    this.options = {
      storageKey: 'theme',
      defaultTheme: 'light',
      onChange: null,
      ...options
    };
    this.init();
  }

  init() {
    const savedTheme = localStorage.getItem(this.options.storageKey);
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (savedTheme) {
      this.setTheme(savedTheme);
    } else if (prefersDark) {
      this.setTheme('dark');
    } else {
      this.setTheme(this.options.defaultTheme);
    }

    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (!localStorage.getItem(this.options.storageKey)) {
        this.setTheme(e.matches ? 'dark' : 'light');
      }
    });
  }

  setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(this.options.storageKey, theme);

    if (this.options.onChange) {
      this.options.onChange(theme);
    }
  }

  toggle() {
    const current = document.documentElement.getAttribute('data-theme');
    this.setTheme(current === 'dark' ? 'light' : 'dark');
  }

  getTheme() {
    return document.documentElement.getAttribute('data-theme') || this.options.defaultTheme;
  }
}

// ========================================
// AUTO-INIT COMPONENTS
// ========================================

function initComponents() {
  // Auto-init tooltips
  document.querySelectorAll('[data-tooltip]').forEach(el => {
    new Tooltip(el, el.dataset.tooltip, {
      placement: el.dataset.tooltipPlacement || 'top'
    });
  });

  // Auto-init dropdowns
  document.querySelectorAll('[data-dropdown-trigger]').forEach(trigger => {
    const menuId = trigger.dataset.dropdownTrigger;
    const menu = document.getElementById(menuId);
    if (menu) {
      new Dropdown(trigger, menu);
    }
  });

  // Auto-init modals
  document.querySelectorAll('[data-modal-trigger]').forEach(trigger => {
    const modalId = trigger.dataset.modalTrigger;
    const modal = document.getElementById(modalId);
    if (modal) {
      const modalInstance = new Modal(modal);
      trigger.addEventListener('click', () => modalInstance.open());
    }
  });

  // Auto-init tabs
  document.querySelectorAll('[data-tabs]').forEach(container => {
    new Tabs(container);
  });

  // Auto-init accordions
  document.querySelectorAll('[data-accordion]').forEach(container => {
    new Accordion(container, {
      allowMultiple: container.dataset.accordionMultiple === 'true'
    });
  });

  // Auto-init ratings
  document.querySelectorAll('[data-rating]').forEach(container => {
    new Rating(container, {
      value: parseInt(container.dataset.ratingValue) || 0,
      maxRating: parseInt(container.dataset.ratingMax) || 5,
      readOnly: container.dataset.ratingReadonly === 'true'
    });
  });

  // Auto-init copy buttons
  document.querySelectorAll('[data-copy]').forEach(btn => {
    btn.addEventListener('click', () => {
      const text = btn.dataset.copy;
      copyToClipboard(text);
    });
  });
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initComponents);
} else {
  initComponents();
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    Dropdown,
    Modal,
    Tabs,
    Toggle,
    Tooltip,
    Toast,
    Accordion,
    Rating,
    SearchInput,
    ThemeToggle,
    copyToClipboard,
    initComponents
  };
}

// Export for ES modules
export {
  Dropdown,
  Modal,
  Tabs,
  Toggle,
  Tooltip,
  Toast,
  Accordion,
  Rating,
  SearchInput,
  ThemeToggle,
  copyToClipboard,
  initComponents
};
