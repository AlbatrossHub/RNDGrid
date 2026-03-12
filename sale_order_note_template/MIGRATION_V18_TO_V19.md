# Odoo 18 → 19 Migration Analysis: sale_order_note_template

## Executive Summary

This document analyzes the `sale_order_note_template` addon for Odoo 19 compatibility and provides an implementation plan. The addon failed to install in Odoo 19 due to a **critical blocker** (now fixed) and may need additional compatibility verification.

---

## 1. Critical Blocker (FIXED)

### Error: `ValueError: Unicode strings with encoding declaration are not supported`

**Root Cause:**  
The module's `static/description/index.html` contained an XML encoding declaration on line 1:

```html
<?xml version="1.0" encoding="utf-8" ?>
```

When Odoo 19 loads a module, it reads the description and passes it to `lxml.html.document_fromstring()`. The lxml library rejects **Unicode strings** that contain encoding declarations—this is a known lxml restriction to prevent parsing inconsistencies.

**Fix Applied:**  
- Removed the XML declaration `<?xml version="1.0" encoding="utf-8" ?>`
- Replaced the verbose XHTML DOCTYPE with a simple HTML5 `<!DOCTYPE html>`
- Simplified the `<html>` tag (removed `xmlns` and `xml:lang` attributes)

**Status:** ✅ Fixed in this branch/module.

---

## 2. Odoo 18 → 19 General Breaking Changes (Reference)

From public release notes and community research:

| Area | Change | Relevance to This Addon |
|------|--------|--------------------------|
| **HTTP routes** | `type='json'` → `type='jsonrpc'` | None – no custom controllers |
| **res.partner.title** | Model deprecated/removed | None – addon does not use it |
| **View types** | `tree` → `list` preferred | Low – `view_mode="tree,form"` often still works; view arch already uses `<list>` |
| **Mail templates** | Rendering engine / API changes | **Verify** – uses `mail.template._render_template()` |
| **Module description** | lxml parsing stricter with encoding declarations | **Fixed** – index.html updated |

---

## 3. Module-Specific Analysis

### 3.1 Models

| File | Notes | Action |
|------|-------|--------|
| `models/sale_order.py` | Extends `sale.order` with `terms_template_id`, `want_note`; onchange for template selection. | No change expected |
| `models/sale_terms_template.py` | Uses `mail.template._render_template()` for jinja2-style templating. | **Verify** `_render_template` API in Odoo 19 |
| `models/mail_render_mixin.py` | Defines `mail.render.mixin` but **not imported** in `models/__init__.py` | Dead code – consider removal |

### 3.2 Views and Reports

| File | Notes | Action |
|------|-------|--------|
| `views/sale_views.xml` | Inherits `sale.view_order_form`, adds fields before `note`. | Verify xpath targets still exist in Odoo 19 sale module |
| `views/sale_terms_template.xml` | Uses `view_mode="tree,form"` and `<list>`. | Usually compatible; switch to `list` if needed |
| `report/sale_report_templates.xml` | Inherits `sale.report_saleorder_document` and `sale.report_saleorder_pro_forma`; uses `doc.want_note`, `doc.company_id.terms_type`, etc. | **Verify** xpaths and `terms_type` availability in Odoo 19 |

### 3.3 Dependencies

- `sale_management` – standard Odoo module, present in Odoo 19.
- No custom Python packages beyond core Odoo.

---

## 4. Implementation Plan

### Phase 1: Unblock Installation (DONE)

- [x] Remove XML encoding declaration from `static/description/index.html`
- [x] Simplify DOCTYPE and HTML tag

### Phase 2: Post-Install Verification

After install succeeds:

1. **Test installation**
   - Install the module in Odoo 19.
   - Confirm no errors during load/upgrade.

2. **Test core flow**
   - Create a terms template with jinja2 placeholders (e.g. `{{ object.name }}`).
   - Create a sale order, select the template, and confirm `note` is filled correctly.
   - Toggle “Add terms in PDF?” and print the quotation PDF.
   - Confirm terms appear/hide as expected.

3. **Check report layout**
   - Verify xpaths in `sale_report_templates.xml` match Odoo 19’s `sale.report_saleorder_document`.
   - Confirm `doc.company_id.terms_type` exists in your Odoo 19 build (from base/company or account).

4. **Mail template API**
   - If `_render_template` was changed in Odoo 19, adapt `sale_terms_template.get_value()` to the new API.
   - Check whether Odoo 19 expects QWeb-only for email-related rendering and adjust templates if needed.

### Phase 3: Optional Cleanup

- [ ] Remove or integrate `models/mail_render_mixin.py` if unused
- [ ] Replace `view_mode="tree,form"` with `view_mode="list,form"` if Odoo 19 prefers `list`
- [ ] Update manifest `version` if you want to track the Odoo 19 migration

---

## 5. Files Modified in This Migration

| File | Change |
|------|--------|
| `static/description/index.html` | Removed XML declaration; simplified DOCTYPE and `<html>` for lxml compatibility |

---

## 6. References

- [Odoo 19 Release Notes](https://www.odoo.com/odoo-19-release-notes)
- [lxml: Unicode strings with encoding declaration](https://bugs.launchpad.net/lxml/+bug/613302)
- [Odoo 17 similar issue: ValueError with etree.fromstring](https://github.com/odoo/odoo/issues/163465)
- OCA `sale_order_note_template` (original 14.0/16.0 base)

---

*Document generated for migration analysis. Re-run tests after any Odoo 19 core updates.*
