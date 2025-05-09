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

    // Search functionality
    $("#searchInput").on("keyup", function() {
        var value = $(this).val().toLowerCase();
        $("#staffTable tbody tr").filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
    });

    // Role filter
    $("#roleFilter").change(function(){
        var filter = $(this).val().toLowerCase();
        $("#staffTable tbody tr").each(function(){
            var role = $(this).find("td:eq(3)").text().toLowerCase();
            $(this).toggle(filter === "" || role.indexOf(filter) > -1);
        });
    });    

    // Edit modal handler
    $('#editStaffModal').on('show.bs.modal', function(event) {
        var button = $(event.relatedTarget);
        var id = button.data('id');
        var name = button.data('name');
        var email = button.data('email');
        var role = button.data('role');
    
        var modal = $(this);
        modal.find('#edit_staff_id').val(id);
        modal.find('#display_staff_id').text(id);  // Display ID as text
        modal.find('#edit_full_name').val(name);
        modal.find('#edit_email').val(email);
        modal.find('#edit_role').val(role);
    });

    // Delete modal handler
    $('#deleteStaffModal').on('show.bs.modal', function(event) {
        var button = $(event.relatedTarget);
        var id = button.data('id');
        var name = button.closest('tr').find('td:eq(1)').text();
        
        var modal = $(this);
        modal.find('#delete_staff_id').val(id);
        modal.find('#delete_staff_name').text(name);
    });

});
