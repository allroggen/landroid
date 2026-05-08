class WorxVisionCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._initialized = false;
  }

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
      throw new Error("Entity (lawn_mower.*) is required");
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

  _buildActionButton(label, icon, serviceName) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "action";
    button.textContent = label;
    button.title = label;
    button.addEventListener("click", () => {
      this._hass.callService("lawn_mower", serviceName, {
        entity_id: this._config.entity,
      });
    });

    const iconEl = document.createElement("ha-icon");
    iconEl.setAttribute("icon", icon);
    button.prepend(iconEl);
    return button;
  }

  _initCard() {
    if (this._initialized) {
      return;
    }

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

    this._card = document.createElement("ha-card");
    const content = document.createElement("div");
    content.className = "content";

    this._missing = document.createElement("div");
    this._missing.className = "missing";
    this._missing.hidden = true;

    this._rows = document.createElement("div");
    this._rows.className = "rows";
    this._values = {};
    const rows = [
      ["Mower", "mower"],
      ["Status", "status"],
      ["Battery", "battery"],
      ["Schedule", "schedule"],
    ];
    for (const [label, key] of rows) {
      const row = this._buildInfoRow(label, "n/a");
      this._values[key] = row.querySelector(".value");
      this._rows.append(row);
    }

    this._actions = document.createElement("div");
    this._actions.className = "actions";
    this._actions.append(
      this._buildActionButton("Start", "mdi:play", "start_mowing"),
      this._buildActionButton("Pause", "mdi:pause", "pause"),
      this._buildActionButton("Dock", "mdi:home-import-outline", "dock")
    );

    content.append(this._missing, this._rows, this._actions);
    this._card.append(content);
    this.shadowRoot.append(style, this._card);
    this._initialized = true;
  }

  _render() {
    if (!this._hass || !this._config) {
      return;
    }
    this._initCard();

    const mower = this._hass.states[this._config.entity];
    const { battery, status, schedule } = this._getRelatedEntities(
      this._config.entity
    );
    this._card.header = this._config.name || "Worx Vision";

    if (!mower) {
      this._missing.textContent = `Entity not found: ${this._config.entity}`;
      this._missing.hidden = false;
      this._rows.hidden = true;
      this._actions.hidden = true;
      return;
    }

    this._missing.hidden = true;
    this._rows.hidden = false;
    this._actions.hidden = false;
    this._values.mower.textContent = mower.state || "unknown";
    this._values.status.textContent = status?.state || "n/a";
    this._values.battery.textContent = battery?.state
      ? `${battery.state}%`
      : "n/a";
    this._values.schedule.textContent = schedule?.state || "n/a";
  }

  _getRelatedEntities(entityId) {
    const objectId = entityId.split(".")[1] || "";
    return {
      battery: this._hass.states[`sensor.${objectId}_battery`],
      status: this._hass.states[`sensor.${objectId}_status`],
      schedule: this._hass.states[`switch.${objectId}_schedule`],
    };
  }
}

class WorxVisionCardEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._onEntityChange = this._onEntityChange.bind(this);
    this._onNameChange = this._onNameChange.bind(this);
    this._initEditor();
  }

  setConfig(config) {
    this._config = config || {};
    this._updateInputs();
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

  _initEditor() {
    this.shadowRoot.innerHTML = `
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

    this._entityInput = this.shadowRoot.getElementById("entity");
    this._nameInput = this.shadowRoot.getElementById("name");
    this._entityInput.addEventListener("change", this._onEntityChange);
    this._nameInput.addEventListener("change", this._onNameChange);
  }

  _updateInputs() {
    if (!this._entityInput || !this._nameInput) {
      return;
    }
    this._entityInput.value = this._config?.entity || "";
    this._nameInput.value = this._config?.name || "";
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
