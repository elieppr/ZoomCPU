"use strict";
import OneByte from "./1byte.js";
import SustainableWebDesign from "./sustainable-web-design.js";
import {
  GLOBAL_GRID_INTENSITY,
  RENEWABLES_GRID_INTENSITY
} from "./constants/index.js";
import { parseOptions } from "./helpers/index.js";
class CO2 {
  constructor(options) {
    this.model = new SustainableWebDesign();
    if ((options == null ? void 0 : options.model) === "1byte") {
      this.model = new OneByte();
    } else if ((options == null ? void 0 : options.model) === "swd") {
      this.model = new SustainableWebDesign();
    } else if (options == null ? void 0 : options.model) {
      throw new Error(`"${options.model}" is not a valid model. Please use "1byte" for the OneByte model, and "swd" for the Sustainable Web Design model.
See https://developers.thegreenwebfoundation.org/co2js/models/ to learn more about the models available in CO2.js.`);
    }
    this._segment = (options == null ? void 0 : options.results) === "segment";
  }
  perByte(bytes, green = false) {
    return this.model.perByte(bytes, green, this._segment);
  }
  perVisit(bytes, green = false) {
    var _a;
    if ((_a = this.model) == null ? void 0 : _a.perVisit) {
      return this.model.perVisit(bytes, green, this._segment);
    } else {
      throw new Error(`The perVisit() method is not supported in the model you are using. Try using perByte() instead.
See https://developers.thegreenwebfoundation.org/co2js/methods/ to learn more about the methods available in CO2.js.`);
    }
  }
  perByteTrace(bytes, green = false, options = {}) {
    var _a, _b, _c, _d, _e, _f, _g, _h, _i;
    let adjustments = {};
    if (options) {
      adjustments = parseOptions(options);
    }
    return {
      co2: this.model.perByte(bytes, green, this._segment, adjustments),
      green,
      variables: {
        description: "Below are the variables used to calculate this CO2 estimate.",
        bytes,
        gridIntensity: {
          description: "The grid intensity (grams per kilowatt-hour) used to calculate this CO2 estimate.",
          network: (_c = (_b = (_a = adjustments == null ? void 0 : adjustments.gridIntensity) == null ? void 0 : _a.network) == null ? void 0 : _b.value) != null ? _c : GLOBAL_GRID_INTENSITY,
          dataCenter: green ? RENEWABLES_GRID_INTENSITY : (_f = (_e = (_d = adjustments == null ? void 0 : adjustments.gridIntensity) == null ? void 0 : _d.dataCenter) == null ? void 0 : _e.value) != null ? _f : GLOBAL_GRID_INTENSITY,
          production: GLOBAL_GRID_INTENSITY,
          device: (_i = (_h = (_g = adjustments == null ? void 0 : adjustments.gridIntensity) == null ? void 0 : _g.device) == null ? void 0 : _h.value) != null ? _i : GLOBAL_GRID_INTENSITY
        }
      }
    };
  }
  perVisitTrace(bytes, green = false, options = {}) {
    var _a, _b, _c, _d, _e, _f, _g, _h, _i, _j, _k, _l, _m;
    if ((_a = this.model) == null ? void 0 : _a.perVisit) {
      let adjustments = {};
      if (options) {
        adjustments = parseOptions(options);
      }
      return {
        co2: this.model.perVisit(bytes, green, this._segment, adjustments),
        green,
        variables: {
          description: "Below are the variables used to calculate this CO2 estimate.",
          bytes,
          gridIntensity: {
            description: "The grid intensity (grams per kilowatt-hour) used to calculate this CO2 estimate.",
            network: (_d = (_c = (_b = adjustments == null ? void 0 : adjustments.gridIntensity) == null ? void 0 : _b.network) == null ? void 0 : _c.value) != null ? _d : GLOBAL_GRID_INTENSITY,
            dataCenter: green ? RENEWABLES_GRID_INTENSITY : (_g = (_f = (_e = adjustments == null ? void 0 : adjustments.gridIntensity) == null ? void 0 : _e.dataCenter) == null ? void 0 : _f.value) != null ? _g : GLOBAL_GRID_INTENSITY,
            production: GLOBAL_GRID_INTENSITY,
            device: (_j = (_i = (_h = adjustments == null ? void 0 : adjustments.gridIntensity) == null ? void 0 : _h.device) == null ? void 0 : _i.value) != null ? _j : GLOBAL_GRID_INTENSITY
          },
          dataReloadRatio: (_k = adjustments == null ? void 0 : adjustments.dataReloadRatio) != null ? _k : 0.02,
          firstVisitPercentage: (_l = adjustments == null ? void 0 : adjustments.firstVisitPercentage) != null ? _l : 0.75,
          returnVisitPercentage: (_m = adjustments == null ? void 0 : adjustments.returnVisitPercentage) != null ? _m : 0.25
        }
      };
    } else {
      throw new Error(`The perVisitDetailed() method is not supported in the model you are using. Try using perByte() instead.
See https://developers.thegreenwebfoundation.org/co2js/methods/ to learn more about the methods available in CO2.js.`);
    }
  }
  perDomain(pageXray, greenDomains) {
    const co2PerDomain = [];
    for (let domain of Object.keys(pageXray.domains)) {
      let co2;
      if (greenDomains && greenDomains.indexOf(domain) > -1) {
        co2 = this.perByte(pageXray.domains[domain].transferSize, true);
      } else {
        co2 = this.perByte(pageXray.domains[domain].transferSize);
      }
      co2PerDomain.push({
        domain,
        co2,
        transferSize: pageXray.domains[domain].transferSize
      });
    }
    co2PerDomain.sort((a, b) => b.co2 - a.co2);
    return co2PerDomain;
  }
  perPage(pageXray, green) {
    const domainCO2 = this.perDomain(pageXray, green);
    let totalCO2 = 0;
    for (let domain of domainCO2) {
      totalCO2 += domain.co2;
    }
    return totalCO2;
  }
  perContentType(pageXray, greenDomains) {
    const co2PerContentType = {};
    for (let asset of pageXray.assets) {
      const domain = new URL(asset.url).domain;
      const transferSize = asset.transferSize;
      const co2ForTransfer = this.perByte(transferSize, greenDomains && greenDomains.indexOf(domain) > -1);
      const contentType = asset.type;
      if (!co2PerContentType[contentType]) {
        co2PerContentType[contentType] = { co2: 0, transferSize: 0 };
      }
      co2PerContentType[contentType].co2 += co2ForTransfer;
      co2PerContentType[contentType].transferSize += transferSize;
    }
    const all = [];
    for (let type of Object.keys(co2PerContentType)) {
      all.push({
        type,
        co2: co2PerContentType[type].co2,
        transferSize: co2PerContentType[type].transferSize
      });
    }
    all.sort((a, b) => b.co2 - a.co2);
    return all;
  }
  dirtiestResources(pageXray, greenDomains) {
    const allAssets = [];
    for (let asset of pageXray.assets) {
      const domain = new URL(asset.url).domain;
      const transferSize = asset.transferSize;
      const co2ForTransfer = this.perByte(transferSize, greenDomains && greenDomains.indexOf(domain) > -1);
      allAssets.push({ url: asset.url, co2: co2ForTransfer, transferSize });
    }
    allAssets.sort((a, b) => b.co2 - a.co2);
    return allAssets.slice(0, allAssets.length > 10 ? 10 : allAssets.length);
  }
  perParty(pageXray, greenDomains) {
    let firstParty = 0;
    let thirdParty = 0;
    const firstPartyRegEx = pageXray.firstPartyRegEx;
    for (let d of Object.keys(pageXray.domains)) {
      if (!d.match(firstPartyRegEx)) {
        thirdParty += this.perByte(pageXray.domains[d].transferSize, greenDomains && greenDomains.indexOf(d) > -1);
      } else {
        firstParty += this.perByte(pageXray.domains[d].transferSize, greenDomains && greenDomains.indexOf(d) > -1);
      }
    }
    return { firstParty, thirdParty };
  }
}
var co2_default = CO2;
export {
  CO2,
  co2_default as default
};
