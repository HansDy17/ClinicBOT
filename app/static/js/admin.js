$(document).ready(function(){
    $("#searchInput").on("keyup", function() {
        var value = $(this).val().toLowerCase();
        $("#appointmentsTable tbody tr").filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
    });
    
    // Date filter functionality
    $("#dateFilter").change(function(){
        var filterDate = $(this).val();
        if(filterDate) {
            $("#appointmentsTable tbody tr").each(function(){
                var rowDate = $(this).find("td:eq(3)").text().trim();
                $(this).toggle(rowDate === filterDate);
            });
        } else {
            $("#appointmentsTable tbody tr").show();
        }
    });
});
