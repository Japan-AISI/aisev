(() => {
  const storageKey = "automatedRtLang";
  const textNodeRegistry = new Map();
  let config = {
    messages: { ja: {}, en: {} },
    textMap: {},
    attributes: [],
    onLanguageChange: [],
  };
  let currentLang = (typeof window !== "undefined" && window.localStorage)
    ? localStorage.getItem(storageKey) || "ja"
    : "ja";

  function getMessage(lang, key) {
    if (!config.messages) return key;
    const parts = key.split(".");
    const traverse = (obj) => parts.reduce((acc, part) => (acc && acc[part] !== undefined ? acc[part] : undefined), obj);
    let value = traverse(config.messages[lang]);
    if (value === undefined) {
      value = traverse(config.messages.ja);
    }
    return typeof value === "string" ? value : key;
  }

  function resolvePlaceholders(message, replacements = {}) {
    return message.replace(/\{\{\s*(\w+)\s*\}\}/g, (_, key) => {
      return Object.prototype.hasOwnProperty.call(replacements, key)
        ? replacements[key]
        : `{{${key}}}`;
    });
  }

  function findTextNodes(baseText) {
    if (!baseText) return [];
    if (textNodeRegistry.has(baseText)) {
      return textNodeRegistry.get(baseText);
    }
    const nodes = [];
    if (typeof document !== "undefined") {
      const walker = document.createTreeWalker(
        document.body,
        NodeFilter.SHOW_TEXT,
        {
          acceptNode(node) {
            const parent = node.parentNode;
            if (!parent) return NodeFilter.FILTER_REJECT;
            const parentName = parent.nodeName.toLowerCase();
            if (parentName === "script" || parentName === "style") {
              return NodeFilter.FILTER_REJECT;
            }
            return node.textContent.trim() === baseText
              ? NodeFilter.FILTER_ACCEPT
              : NodeFilter.FILTER_SKIP;
          },
        }
      );
      let current = walker.nextNode();
      while (current) {
        nodes.push(current);
        current = walker.nextNode();
      }
    }
    textNodeRegistry.set(baseText, nodes);
    return nodes;
  }

  function applyLanguage() {
    if (typeof document === "undefined") return;
    document.documentElement.lang = currentLang;

    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const key = el.getAttribute("data-i18n");
      if (!key) return;
      el.textContent = getMessage(currentLang, key);
    });

    document.querySelectorAll("[data-i18n-html]").forEach((el) => {
      const key = el.getAttribute("data-i18n-html");
      if (!key) return;
      el.innerHTML = getMessage(currentLang, key);
    });

    document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
      const key = el.getAttribute("data-i18n-placeholder");
      if (!key) return;
      el.setAttribute("placeholder", getMessage(currentLang, key));
    });

    Object.entries(config.textMap || {}).forEach(([baseText, translations]) => {
      const nodes = findTextNodes(baseText);
      const message = translations[currentLang] ?? translations.ja ?? baseText;
      nodes.forEach((node) => {
        node.textContent = message;
      });
    });

    (config.attributes || []).forEach(({ selector, attr, key, values }) => {
      const value = key ? getMessage(currentLang, key) : values?.[currentLang];
      if (value === undefined) return;
      document.querySelectorAll(selector).forEach((el) => {
        el.setAttribute(attr, value);
      });
    });

    document.querySelectorAll("[data-lang]").forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.lang === currentLang);
    });

    (config.onLanguageChange || []).forEach((callback) => {
      if (typeof callback === "function") {
        callback(currentLang);
      }
    });
  }

  function register(newConfig) {
    textNodeRegistry.clear();
    config = {
      messages: newConfig.messages || { ja: {}, en: {} },
      textMap: newConfig.textMap || {},
      attributes: newConfig.attributes || [],
      onLanguageChange: newConfig.onLanguageChange || [],
    };
    applyLanguage();
  }

  function setLanguage(lang) {
    if (lang !== "ja" && lang !== "en") return;
    currentLang = lang;
    if (typeof window !== "undefined" && window.localStorage) {
      localStorage.setItem(storageKey, currentLang);
    }
    applyLanguage();
  }

  function getLanguage() {
    return currentLang;
  }

  function translate(key, replacements) {
    const message = getMessage(currentLang, key);
    return resolvePlaceholders(message, replacements);
  }

  window.automatedRtI18n = {
    register,
    setLanguage,
    getLanguage,
    t: translate,
  };

  if (typeof document !== "undefined") {
    document.addEventListener("DOMContentLoaded", () => {
      applyLanguage();
    });
  }
})();
