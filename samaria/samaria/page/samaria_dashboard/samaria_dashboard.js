/**
 * Samaria Executive Dashboard — Desk Page Controller
 * Frappe v15
 */

frappe.pages["samaria_dashboard"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Samaria Executive Dashboard"),
		single_column: true
	});
	frappe.breadcrumbs.add("Samaria");
	new SamariaDashboard(page);
};

class SamariaDashboard {
	constructor(page) {
		this.page    = page;
		this.filters = { customer: null, from_date: null, to_date: null };
		this.init();
	}

	init() {
		this._setup_actions();
		this._setup_filters();
		this._render_skeleton();
		this.refresh();
	}

	// ── Actions ─────────────────────────────────────────────────────────
	_setup_actions() {
		this.page.set_primary_action(__("New Dispatch"), () => frappe.new_doc("Aggregate Delivery"), "add");
		this.page.add_secondary_action(__("New Cement Lifting"), () => frappe.new_doc("Cement Lifting"));

		this.page.add_inner_button(__("New Sales Agreement"), () => frappe.new_doc("Sales Agreement"), __("Quick Actions"));
		this.page.add_inner_button(__("New Medical Request"),  () => frappe.new_doc("Medical Request"),  __("Quick Actions"));

		[
			[__("Aggregate Dispatch Report"),      "Aggregate Project Dispatch Report"],
			[__("Cement Lifting Report"),           "Cement Project Lifting and Balance Report"],
			[__("Medical Inventory Report"),        "Medical Project Inventory Report"],
			[__("Financial Summary Report"),        "Project Financial Summary Report"],
		].forEach(([label, report]) => {
			this.page.add_inner_button(label, () => frappe.set_route("query-report", report), __("Reports"));
		});
	}

	// ── Filter fields ────────────────────────────────────────────────────
	_setup_filters() {
		this._f_customer = this.page.add_field({
			fieldname: "customer", label: __("Customer / Project"),
			fieldtype: "Link", options: "Customer",
			change: () => { this.filters.customer = this._f_customer.get_value(); this.refresh(); }
		});
		this._f_from = this.page.add_field({
			fieldname: "from_date", label: __("From Date"), fieldtype: "Date",
			change: () => { this.filters.from_date = this._f_from.get_value(); this.refresh(); }
		});
		this._f_to = this.page.add_field({
			fieldname: "to_date", label: __("To Date"), fieldtype: "Date",
			change: () => { this.filters.to_date = this._f_to.get_value(); this.refresh(); }
		});
	}

	// ── Skeleton layout ──────────────────────────────────────────────────
	_render_skeleton() {
		this.$wrap = $(`
			<div class="samaria-db">
				<div class="samaria-kpi-row" id="s-kpis">
					<p class="text-muted">${__("Loading KPIs…")}</p>
				</div>
				<div class="samaria-chart-row">
					<div class="samaria-chart-card">
						<h4 class="samaria-card-title">${__("Aggregate Dispatch Trend (m³)")}</h4>
						<div id="s-chart-agg" style="min-height:220px;"></div>
					</div>
					<div class="samaria-chart-card">
						<h4 class="samaria-card-title">${__("Cement Lifted by Factory")}</h4>
						<div id="s-chart-cem" style="min-height:220px;"></div>
					</div>
				</div>
				<div class="samaria-table-row">
					<div class="samaria-table-card">
						<h4 class="samaria-card-title">
							${__("Recent Aggregate Deliveries")}
							<a href="/app/aggregate-delivery" class="samaria-viewall">${__("View All →")}</a>
						</h4>
						<div id="s-tbl-agg"></div>
					</div>
					<div class="samaria-table-card">
						<h4 class="samaria-card-title">
							${__("Recent Cement Liftings")}
							<a href="/app/cement-lifting" class="samaria-viewall">${__("View All →")}</a>
						</h4>
						<div id="s-tbl-cem"></div>
					</div>
				</div>
			</div>
		`).appendTo(this.page.main);
	}

	// ── Refresh ──────────────────────────────────────────────────────────
	refresh() {
		frappe.call({
			method: "samaria.samaria.page.samaria_dashboard.samaria_dashboard.get_dashboard_data",
			args: this.filters,
			callback: (r) => {
				if (!r.message) return;
				const d = r.message;
				this._render_kpis(d.metrics);
				this._render_charts(d.charts);
				this._render_tables(d);
			}
		});
	}

	// ── KPI Cards ────────────────────────────────────────────────────────
	_render_kpis(m) {
		const fmt = (n) => format_number(n, null, 2);
		const cards = [
			{
				color: "orange",
				title: __("Aggregate Volume"), badge: `${m.aggregate.total_dispatches} ${__("Loads")}`,
				value: `${m.aggregate.delivered_volume} <small>m³</small>`,
				sub:   `${__("Net Margin:")} <b>ETB ${fmt(m.aggregate.net_profit)}</b>`
			},
			{
				color: "green",
				title: __("Cement Lifted"), badge: `${m.cement.total_liftings} ${__("Tickets")}`,
				value: `${m.cement.total_weight_tons} <small>Tons</small>`,
				sub:   `${__("Shortage Penalty:")} <b>ETB ${fmt(m.cement.total_penalties)}</b>`
			},
			{
				color: "red",
				title: __("Medical Batches"), badge: `${m.medical.quarantined_batches} ${__("Quarantine")}`,
				value: `${m.medical.active_batches} <small>${__("Active")}</small>`,
				sub:   `${__("Near Expiry:")} <b>${m.medical.near_expiry_batches}</b> | ${__("Pending Req:")} <b>${m.medical.pending_requests}</b>`
			},
			{
				color: "purple",
				title: __("Active Contracts"), badge: `${m.commercial.active_agreements} ${__("Active")}`,
				value: `<small>ETB</small> ${fmt(m.commercial.total_contract_value)}`,
				sub:   __("Aggregate, Cement &amp; Medical Agreements")
			},
		];

		const html = cards.map(c => `
			<div class="samaria-kpi-card samaria-kpi-${c.color}">
				<div class="samaria-kpi-head">
					<span class="samaria-kpi-title">${c.title}</span>
					<span class="indicator ${c.color}">${c.badge}</span>
				</div>
				<div class="samaria-kpi-value">${c.value}</div>
				<div class="samaria-kpi-sub">${c.sub}</div>
			</div>
		`).join("");
		this.$wrap.find("#s-kpis").html(html);
	}

	// ── Charts ───────────────────────────────────────────────────────────
	_render_charts(charts) {
		// Aggregate trend
		const $agg = this.$wrap.find("#s-chart-agg").empty();
		if (charts.aggregate_trend.labels.length) {
			new frappe.Chart($agg[0], {
				data: charts.aggregate_trend,
				type: "line", height: 210,
				colors: ["#f97316"],
				lineOptions: { hideDots: 0, regionFill: 1 }
			});
		} else {
			$agg.html(`<p class="text-muted text-center" style="padding:4rem 0">${__("No data")}</p>`);
		}

		// Cement by factory
		const $cem = this.$wrap.find("#s-chart-cem").empty();
		if (charts.cement_by_factory.labels.length) {
			new frappe.Chart($cem[0], {
				data: charts.cement_by_factory,
				type: "donut", height: 210,
				colors: ["#10b981","#06b6d4","#3b82f6","#8b5cf6","#f59e0b"]
			});
		} else {
			$cem.html(`<p class="text-muted text-center" style="padding:4rem 0">${__("No data")}</p>`);
		}
	}

	// ── Tables ───────────────────────────────────────────────────────────
	_render_tables(d) {
		// Aggregate
		const $at = this.$wrap.find("#s-tbl-agg");
		if (d.recent_dispatches && d.recent_dispatches.length) {
			const rows = d.recent_dispatches.map(r => `
				<tr>
					<td><a href="/app/aggregate-delivery/${r.name}"><b>${r.name}</b></a><br>
						<small class="text-muted">${r.customer_name || ""}</small></td>
					<td>${r.item_name || "Aggregate"}<br>
						<small class="text-muted">${__("Pad:")} ${r.pad_number || "-"}</small></td>
					<td><b>${r.delivered_volume || 0}</b> m³</td>
					<td><span class="indicator-pill ${["Delivered","Settled"].includes(r.status) ? "green" : "blue"} filterable">${r.status}</span></td>
				</tr>`).join("");
			$at.html(`<table class="table table-sm samaria-mini-table">
				<thead><tr><th>${__("Dispatch")}</th><th>${__("Material")}</th><th>${__("Delivered")}</th><th>${__("Status")}</th></tr></thead>
				<tbody>${rows}</tbody></table>`);
		} else {
			$at.html(`<p class="text-muted text-center" style="padding:2rem 0">${__("No recent dispatches")}</p>`);
		}

		// Cement
		const $ct = this.$wrap.find("#s-tbl-cem");
		if (d.recent_liftings && d.recent_liftings.length) {
			const rows = d.recent_liftings.map(r => `
				<tr>
					<td><a href="/app/cement-lifting/${r.name}"><b>${r.name}</b></a><br>
						<small class="text-muted">${r.customer_name || ""}</small></td>
					<td>${r.factory || "-"}<br>
						<small class="text-muted">${r.lifting_date || ""}</small></td>
					<td><b>${r.buyer_weighbridge_qty || 0}</b> Tons</td>
					<td><span class="indicator-pill ${["Delivered","Verified"].includes(r.status) ? "green" : "blue"} filterable">${r.status}</span></td>
				</tr>`).join("");
			$ct.html(`<table class="table table-sm samaria-mini-table">
				<thead><tr><th>${__("Lifting")}</th><th>${__("Factory/Date")}</th><th>${__("Weight")}</th><th>${__("Status")}</th></tr></thead>
				<tbody>${rows}</tbody></table>`);
		} else {
			$ct.html(`<p class="text-muted text-center" style="padding:2rem 0">${__("No recent liftings")}</p>`);
		}
	}
}
