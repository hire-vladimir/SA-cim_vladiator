require([
    'underscore',
    'jquery',
    'splunkjs/mvc',
    'splunkjs/mvc/tableview',
    'splunkjs/mvc/simplexml/ready!'
], function(_, $, mvc, TableView) {

    // Translations from rangemap results to CSS class
    var ICONS = {
        severe: 'alert-circle',
        elevated: 'alert',
        low: 'check-circle',
	check: 'question-circle',
        star: 'star'
    };

    var RangeMapIconRenderer = TableView.BaseCellRenderer.extend({
        canRender: function(cell) {
            // Only use the cell renderer for the range field
            return cell.field.match(/status|line|is_cim_valid|is_recommended|ir/);
        },
        render: function($td, cell) {
            var icon = 'question';
		if (!(cell.value instanceof Array) && cell.value != null) {
			cell.value = cell.value.split("##");
		}

		for (var v in cell.value) {	
			if (cell.value.hasOwnProperty(v)) { 
				val = cell.value[v].split("!!!");
	
		        if (ICONS.hasOwnProperty(val[0])) {
		       		icon = ICONS[val[0]];
		        }
				
			var needsBreak = (v == cell.value-1) ? "":"<br />";
		        $td.addClass('icon').append(_.template('<div class="multivalue-subcell"><i class="icon-<%-icon%> <%- range %>" title="<%- range %>"></i>&nbsp;<%-text%></div>', {
		        	icon: icon,
		                range: val[0],
				text: (val[1] != undefined) ? val[1] : ""
		            }));
			}
		}
        	}
	});
	
	var viz2target = ['tmy_mv_table', 'v_btool_default_table'];
	for (var v in viz2target) {
		if (mvc.Components.get(viz2target[v]) != undefined) {
			mvc.Components.get(viz2target[v]).getVisualization(function(tableView){
				tableView.table.addCellRenderer(new RangeMapIconRenderer());
				tableView.table.render();
			});
		}
	}
});
