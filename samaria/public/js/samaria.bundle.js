/**
 * Samaria Frappe v16 Desk Bundle
 */

frappe.provide("samaria");

samaria = {
	version: "0.0.1",
	init: function() {
		console.info("[Samaria] Frappe Module v16 initialized.");
	}
};

$(document).on("app_ready", function() {
	samaria.init();
});
