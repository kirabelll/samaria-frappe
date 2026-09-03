/**
 * Samaria Executive Dashboard Page Controller
 * Frappe Framework Version-16
 */

frappe.pages['samaria_dashboard'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __('Samaria Executive Dashboard'),
		single_column: true
	});

	frappe.breadcrumbs.add("Samaria");
	new SamariaDashboard(page);
};

class SamariaDashboard {
	constructor(page) {
		this.page = page;
		this.filters = {
			customer: null,
			from_date: null,
			to_date: null
		};
		this.init();
	}

	init() {
		this.setup_actions();
		this.setup_filter_fields();
		this.render_layout();
		this.refresh();
	}

	setup_actions() {
		// Quick Action Buttons
		this.page.set_primary_action(
			__('New Dispatch'),
			() => frappe.new_doc('Aggregate Delivery'),
			'add'
		);

		this.page.add_secondary_action(
			__('New Cement Lifting'),
			() => frappe.new_doc('Cement Lifting')
		);

		this.page.add_inner_button(__('New Sales Agreement'), () => {
			frappe.new_doc('Sales Agreement');
		}, __('Quick Actions'));

		this.page.add_inner_button(__('Open Project Reports'), () => {
			frappe.set_route('query-report', 'Aggregate Project Dispatch Report');
		}, __('Reports'));

		this.page.add_inner_button(__('Cement Lifting Report'), () => {
			frappe.set_route('query-report', 'Cement Project Lifting and Balance Report');
		}, __('Reports'));

		this.page.add_inner_button(__('Medical Inventory Report'), () => {
			frappe.set_route('query-report', 'Medical Project Inventory Report');
		}, __('Reports'));

		this.page.add_inner_button(__('Financial Summary Report'), () => {
			frappe.set_route('query-report', 'Project Financial Summary Report');
		}, __('Reports'));
	}

	setup_filter_fields() {
		// Customer / Project Filter
		this.customer_field = this.page.add_field({
			fieldname: 'customer',
			label: __('Project / Customer'),
			fieldtype: 'Link',
			options: 'Customer',
			change: () => {
				this.filters.customer = this.customer_field.get_value();
				this.refresh();
			}
		});

		// From Date Filter
		this.from_date_field = this.page.add_field({
			fieldname: 'from_date',
			label: __('From Date'),
			fieldtype: 'Date',
			change: () => {
				this.filters.from_date = this.from_date_field.get_value();
				this.refresh();
			}
		});

		// To Date Filter
		this.to_date_field = this.page.add_field({
			fieldname: 'to_date',
			label: __('To Date'),
			fieldtype: 'Date',
			change: () => {
				this.filters.to_date = this.to_date_field.get_value();
				this.refresh();
			}
		});
	}

	render_layout() {
		this.$container = $(`
			<div class="samaria-dashboard-container">
				<!-- KPI Cards Row -->
				<div class="samaria-kpi-grid" id="samaria-kpis">
					<div class="text-muted">${__('Loading KPI metrics...')}</div>
				</div>

				<!-- Charts Row -->
				<div class="samaria-charts-grid">
					<div class="samaria-chart-card">
						<h4>${__('Aggregate Dispatch Volume Trend (m³)')}</h4>
						<div id="chart-aggregate-trend" style="min-height: 240px;"></div>
					</div>
					<div class="samaria-chart-card">
						<h4>${__('Cement Lifting Distribution by Factory')}</h4>
						<div id="chart-cement-factory" style="min-height: 240px;"></div>
					</div>
				</div>

				<!-- Tables Row -->
				<div class="samaria-tables-grid">
					<div class="samaria-table-card">
						<h4>
							<span>${__('Recent Aggregate Deliveries')}</span>
							<a href="/app/aggregate-delivery" class="text-muted" style="font-size: 0.8rem;">${__('View All')} &rarr;</a>
						</h4>
						<div id="recent-aggregate-table"></div>
					</div>
					<div class="samaria-table-card">
						<h4>
							<span>${__('Recent Cement Liftings')}</span>
							<a href="/app/cement-lifting" class="text-muted" style="font-size: 0.8rem;">${__('View All')} &rarr;</a>
						</h4>
						<div id="recent-cement-table"></div>
					</div>
				</div>
			</div>
		`).appendTo(this.page.main);
	}

	refresh() {
		frappe.call({
			method: 'samaria.samaria.page.samaria_dashboard.samaria_dashboard.get_dashboard_data',
			args: {
				customer: this.filters.customer,
				from_date: this.filters.from_date,
				to_date: this.filters.to_date
			},
			callback: (r) => {
				if (r.message) {
					this.render_kpis(r.message.metrics);
					this.render_charts(r.message.charts);
					this.render_tables(r.message);
				}
			}
		});
	}

	render_kpis(metrics) {
		const m = metrics;
		const html = `
			<div class="samaria-kpi-card orange">
				<div class="samaria-kpi-title">
					<span>${__('Aggregate Volume')}</span>
					<span class="indicator orange">${m.aggregate.total_dispatches} ${__('Loads')}</span>
				</div>
				<div class="samaria-kpi-value">${m.aggregate.delivered_volume} <span style="font-size: 1rem; font-weight: 500;">m³</span></div>
				<div class="samaria-kpi-subtext">
					<span>${__('Net Margin:')} <strong>ETB ${format_number(m.aggregate.net_profit, null, 2)}</strong></span>
				</div>
			</div>

			<div class="samaria-kpi-card emerald">
				<div class="samaria-kpi-title">
					<span>${__('Cement Lifted')}</span>
					<span class="indicator green">${m.cement.total_liftings} ${__('Tickets')}</span>
				</div>
				<div class="samaria-kpi-value">${m.cement.total_weight_tons} <span style="font-size: 1rem; font-weight: 500;">Tons</span></div>
				<div class="samaria-kpi-subtext">
					<span>${__('Shortage Penalty:')} <strong>ETB ${format_number(m.cement.total_penalties, null, 2)}</strong></span>
				</div>
			</div>

			<div class="samaria-kpi-card rose">
				<div class="samaria-kpi-title">
					<span>${__('Medical Batches')}</span>
					<span class="indicator red">${m.medical.quarantined_batches} ${__('Quarantine')}</span>
				</div>
				<div class="samaria-kpi-value">${m.medical.active_batches} <span style="font-size: 1rem; font-weight: 500;">Active</span></div>
				<div class="samaria-kpi-subtext">
					<span>${__('Expiring <90 Days:')} <strong>${m.medical.near_expiry_batches}</strong> | ${__('Pending Req:')} <strong>${m.medical.pending_requests}</strong></span>
				</div>
			</div>

			<div class="samaria-kpi-card purple">
				<div class="samaria-kpi-title">
					<span>${__('Active Contracts')}</span>
					<span class="indicator purple">${m.commercial.active_agreements} ${__('Active')}</span>
				</div>
				<div class="samaria-kpi-value"><span style="font-size: 1.1rem; font-weight: 600;">ETB</span> ${format_number(m.commercial.total_contract_value, null, 2)}</div>
				<div class="samaria-kpi-subtext">
					<span>${__('Aggregate, Cement & Medical Agreements')}</span>
				</div>
			</div>
		`;
		this.$container.find('#samaria-kpis').html(html);
	}

	render_charts(charts) {
		// 1. Aggregate Trend Chart
		const trendData = charts.aggregate_trend;
		const $trendWrapper = this.$container.find('#chart-aggregate-trend');
		$trendWrapper.empty();

		if (trendData.labels && trendData.labels.length > 0) {
			new frappe.Chart($trendWrapper[0], {
				data: trendData,
				type: 'line',
				height: 220,
				colors: ['#f97316'],
				lineOptions: { hideDots: 0, regionFill: 1 }
			});
		} else {
			$trendWrapper.html(`<div class="text-muted text-center" style="padding: 4rem 0;">${__('No aggregate dispatch data in selected range')}</div>`);
		}

		// 2. Cement Distribution Chart
		const cementData = charts.cement_by_factory;
		const $cementWrapper = this.$container.find('#chart-cement-factory');
		$cementWrapper.empty();

		if (cementData.labels && cementData.labels.length > 0) {
			new frappe.Chart($cementWrapper[0], {
				data: cementData,
				type: 'donut',
				height: 220,
				colors: ['#10b981', '#06b6d4', '#3b82f6', '#8b5cf6', '#f59e0b']
			});
		} else {
			$cementWrapper.html(`<div class="text-muted text-center" style="padding: 4rem 0;">${__('No cement lifting records found')}</div>`);
		}
	}

	render_tables(data) {
		// Recent Dispatches Table
		const $aggTable = this.$container.find('#recent-aggregate-table');
		if (data.recent_dispatches && data.recent_dispatches.length > 0) {
			let rows = data.recent_dispatches.map(d => `
				<tr>
					<td>
						<a href="/app/aggregate-delivery/${d.name}"><strong>${d.name}</strong></a><br>
						<small class="text-muted">${d.customer_name || ''}</small>
					</td>
					<td>${d.item_name || 'Aggregate'}<br><small class="text-muted">Pad: ${d.pad_number || '-'}</small></td>
					<td><strong>${d.delivered_volume || 0}</strong> m³</td>
					<td>
						<span class="samaria-badge-sm ${d.status === 'Delivered' || d.status === 'Settled' ? 'green' : 'blue'}">
							${d.status}
						</span>
					</td>
				</tr>
			`).join('');

			$aggTable.html(`
				<table class="samaria-dash-table">
					<thead>
						<tr>
							<th>${__('Dispatch / Site')}</th>
							<th>${__('Material')}</th>
							<th>${__('Delivered')}</th>
							<th>${__('Status')}</th>
						</tr>
					</thead>
					<tbody>${rows}</tbody>
				</table>
			`);
		} else {
			$aggTable.html(`<div class="text-muted text-center" style="padding: 2rem 0;">${__('No recent aggregate dispatches')}</div>`);
		}

		// Recent Cement Liftings Table
		const $cementTable = this.$container.find('#recent-cement-table');
		if (data.recent_liftings && data.recent_liftings.length > 0) {
			let rows = data.recent_liftings.map(c => `
				<tr>
					<td>
						<a href="/app/cement-lifting/${c.name}"><strong>${c.name}</strong></a><br>
						<small class="text-muted">${c.customer_name || ''}</small>
					</td>
					<td>${c.factory || '-'}<br><small class="text-muted">${c.lifting_date || ''}</small></td>
					<td><strong>${c.buyer_weighbridge_qty || 0}</strong> Tons</td>
					<td>
						<span class="samaria-badge-sm ${c.status === 'Delivered' || c.status === 'Verified' ? 'green' : 'blue'}">
							${c.status}
						</span>
					</td>
				</tr>
			`).join('');

			$cementTable.html(`
				<table class="samaria-dash-table">
					<thead>
						<tr>
							<th>${__('Lifting Ref / Buyer')}</th>
							<th>${__('Factory / Date')}</th>
							<th>${__('Weight')}</th>
							<th>${__('Status')}</th>
						</tr>
					</thead>
					<tbody>${rows}</tbody>
				</table>
			`);
		} else {
			$cementTable.html(`<div class="text-muted text-center" style="padding: 2rem 0;">${__('No recent cement liftings')}</div>`);
		}
	}
}
