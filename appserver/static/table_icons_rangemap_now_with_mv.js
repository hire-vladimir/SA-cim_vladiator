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
	check: 'question-circle'
    };

    var RangeMapIconRenderer = TableView.BaseCellRenderer.extend({
        canRender: function(cell) {
            // Only use the cell renderer for the range field
            return cell.field.match(/status|line|is_cim_valid/);
        },
        render: function($td, cell) {
            var icon = 'question';
			
			//debugger;
			
			if (!(cell.value instanceof Array) && cell.value != null) {
			    console.log("data is  array, lets fix it");
			    cell.value = cell.value.split("##");
			}
			console.log("dataset is: ", cell.value)

			for (var v in cell.value) {	
				if (cell.value.hasOwnProperty(v)) { 
					val = cell.value[v].split("!!!");
	
	             	// Fetch the icon for the value
		            if (ICONS.hasOwnProperty(val[0])) {
		                icon = ICONS[val[0]];
		            }
				
					var needsBreak = (v == cell.value-1) ? "":"<br />";
					//debugger;
		            // Create the icon element and add it to the table cell
	
		            $td.addClass('icon').append(_.template('<div class="multivalue-subcell"><i class="icon-<%-icon%> <%- range %>" title="<%- range %>"></i>&nbsp;<%-text%></div>', {
		                icon: icon,
		                range: val[0],
						text: (val[1] != undefined) ? val[1] : ""
		            }) /*+ needsBreak*/);
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
	/*
    mvc.Components.get('tmy_mv_table').getVisualization(function(tableView){
        // Register custom cell renderer
        tableView.table.addCellRenderer(new RangeMapIconRenderer());
        // Force the table to re-render
        tableView.table.render();
    });*/
});
