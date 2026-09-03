/**
 * Samaria Frappe v16 Desk Bundle JS
 * Modern Enterprise Theme & Sidebar Enhancements
 */

frappe.provide("samaria");

samaria = {
	version: "16.0.0",
	init: function() {
		console.info("[Samaria] Frappe Module v16 initialized.");
		this.setup_sidebar_badges();
		this.bind_route_listener();
	},

	setup_sidebar_badges: function() {
		// Adds distinctive division indicators to Frappe v16 Desk sidebar
		const tag_map = {
			"samaria": { tag: "Hub", cls: "hub" },
			"aggregate-operations": { tag: "Quarry", cls: "aggregate" },
			"cement-operations": { tag: "Plant", cls: "cement" },
			"medical-division": { tag: "Pharma", cls: "medical" },
			"agreements-and-commercial": { tag: "B2B", cls: "commercial" },
			"samaria-project-reports": { tag: "Reports", cls: "reports" }
		};

		setTimeout(() => {
			$(".desk-sidebar .standard-sidebar-item").each(function() {
				const route = $(this).attr("item-name") || $(this).data("name") || "";
				const norm_route = route.toLowerCase().replace(/_/g, "-");

				if (tag_map[norm_route] && !$(this).find(".samaria-sidebar-tag").length) {
					const info = tag_map[norm_route];
					$(this).find(".sidebar-item-control, .item-anchor").first().append(
						`<span class="samaria-sidebar-tag ${info.cls}">${info.tag}</span>`
					);
				}
			});
		}, 800);
	},

	bind_route_listener: function() {
		$(document).on("page-change", () => {
			this.setup_sidebar_badges();
		});
	}
};

$(document).on("app_ready", function() {
	samaria.init();
});
