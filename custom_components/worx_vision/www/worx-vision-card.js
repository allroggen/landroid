class WorxVisionCard extends HTMLElement {
  static getConfigElement() {
    return document.createElement("worx-vision-card-editor");
  }

  static getStubConfig(hass, entities) {
    const mower = (entities || []).find((entity) =>
      entity.startsWith("lawn_mower.")
    );
    return {
      type: "custom:worx-vision-card",
      entity: mower || "lawn_mower.my_mower",
      name: "Worx Vision",
    };
  }

  setConfig(config) {
    if (!config || !config.entity) {
      throw new Error("Entity is required");
    }
    this._config = config;
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() {
    return 4;
  }

  _buildInfoRow(label, value) {
    const row = document.createElement("div");
    row.className = "row";

    const key = document.createElement("span");
    key.className = "key";
    key.textContent = label;

    const val = document.createElement("span");
    val.className = "value";
    val.textContent = value;

    row.append(key, val);
    return row;
  }

  _buildActionButton(label, icon, service) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "action";
    button.textContent = label;
    button.title = label;
    button.addEventListener("click", () => {
      this._hass.callService("lawn_mower", service, {
        entity_id: this._config.entity,
      });
    });

    const iconEl = document.createElement("ha-icon");
    iconEl.setAttribute("icon", icon);
    button.prepend(iconEl);
    return button;
  }

  _render() {
    if (!this._hass || !this._config) {
      return;
    }

    const mower = this._hass.states[this._config.entity];
    const objectId = this._config.entity.split(".")[1] || "";
    const battery = this._hass.states[`sensor.${objectId}_battery`];
    const status = this._hass.states[`sensor.${objectId}_status`];
    const schedule = this._hass.states[`switch.${objectId}_schedule`];

    const root = this.shadowRoot || this.attachShadow({ mode: "open" });
    root.innerHTML = "";

    const style = document.createElement("style");
    style.textContent = `
      .content { padding: 16px; }
      .rows { display: grid; gap: 8px; margin-bottom: 12px; }
      .row { display: flex; justify-content: space-between; gap: 12px; }
      .key { color: var(--secondary-text-color); }
      .value { font-weight: 500; text-align: right; }
      .actions { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; }
      .action {
        border: 1px solid var(--divider-color);
        border-radius: 10px;
        background: var(--card-background-color);
        color: var(--primary-text-color);
        padding: 8px 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        cursor: pointer;
      }
      .action:hover { background: var(--secondary-background-color); }
      .missing { color: var(--error-color); }
    `;

    const card = document.createElement("ha-card");
    card.header = this._config.name || "Worx Vision";

    const content = document.createElement("div");
    content.className = "content";

    if (!mower) {
      const missing = document.createElement("div");
      missing.className = "missing";
      missing.textContent = `Entity not found: ${this._config.entity}`;
      content.append(missing);
      card.append(content);
      root.append(style, card);
      return;
    }

    const rows = document.createElement("div");
    rows.className = "rows";
    rows.append(
      this._buildInfoRow("Mäher", mower.state || "unknown"),
      this._buildInfoRow("Status", status?.state || "n/a"),
      this._buildInfoRow("Akku", battery?.state ? `${battery.state}%` : "n/a"),
      this._buildInfoRow("Zeitplan", schedule?.state || "n/a")
    );

    const actions = document.createElement("div");
    actions.className = "actions";
    actions.append(
      this._buildActionButton("Start", "mdi:play", "start_mowing"),
      this._buildActionButton("Pause", "mdi:pause", "pause"),
      this._buildActionButton("Dock", "mdi:home-import-outline", "dock")
    );

    content.append(rows, actions);
    card.append(content);
    root.append(style, card);
  }
}

class WorxVisionCardEditor extends HTMLElement {
  setConfig(config) {
    this._config = config || {};
    this._render();
  }

  _onEntityChange(event) {
    const value = event.target.value;
    this.dispatchEvent(
      new CustomEvent("config-changed", {
        detail: { config: { ...this._config, entity: value } },
        bubbles: true,
        composed: true,
      })
    );
  }

  _onNameChange(event) {
    const value = event.target.value;
    this.dispatchEvent(
      new CustomEvent("config-changed", {
        detail: { config: { ...this._config, name: value } },
        bubbles: true,
        composed: true,
      })
    );
  }

  _render() {
    const root = this.shadowRoot || this.attachShadow({ mode: "open" });
    root.innerHTML = `
      <style>
        .wrapper { display: grid; gap: 12px; padding: 4px 0; }
        label { font-weight: 500; display: grid; gap: 6px; }
        input {
          border: 1px solid var(--divider-color);
          border-radius: 8px;
          padding: 8px;
          background: var(--card-background-color);
          color: var(--primary-text-color);
        }
      </style>
      <div class="wrapper">
        <label>
          Entity (lawn_mower.*)
          <input id="entity" type="text" />
        </label>
        <label>
          Name (optional)
          <input id="name" type="text" />
        </label>
      </div>
    `;

    const entityInput = root.getElementById("entity");
    const nameInput = root.getElementById("name");

    entityInput.value = this._config?.entity || "";
    nameInput.value = this._config?.name || "";
    entityInput.addEventListener("change", this._onEntityChange.bind(this));
    nameInput.addEventListener("change", this._onNameChange.bind(this));
  }
}

customElements.define("worx-vision-card", WorxVisionCard);
customElements.define("worx-vision-card-editor", WorxVisionCardEditor);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "worx-vision-card",
  name: "Worx Vision Card",
  description: "Worx Vision mower controls with status overview.",
  preview: true,
});
