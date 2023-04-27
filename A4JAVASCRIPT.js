$(document).ready(

    function(){
        const fileInput = $("#sdf_file")
        const preview = $("#preview")
      
        fileInput.on("change", function() {
          const file = this.files[0]
          if (file) {
            preview.text(file.name)
          }
        }
        )

        $("#add-btn").click(
            function(){
                $.post("/element-add",
                {
                    element_number: $("#element-number").val(),
                    element_code: $("#element-code").val(),
                    element_name: $("#element-name").val(),
                    color1: $("#color1").val(),
                    color2: $("#color2").val(),
                    color3: $("#color3").val(),
                    radius: $("#radius").val()
                }
                )
            }
        )
        $("#remove-btn").click(
            function()
            {
                $.post("/element-remove",
                {
                    element_code: $("#remove-element-code").val()
                }
                )
            }
        )
        $("#molecule-name-btn").click(
            function()
            {
            $.post("/molecule-name-form",
            {
                molecule_name: $("#molecule-name").val()
            }
            )
            }
        )


        var selectedValue = null
        $("#molecule-select").change( 
            function()
            {
                selectedValue = $(this).val()
                $.post("/molecule-select",
                {
                    molecule_selected: selectedValue
                },
                function(response) {
                    var svg = response.svg;
                    $('#svg-container').html(svg)
                }
                )
                
            }
        )

        $("#button-right").click(
            function()
            {
                $.post("/rotate-right",
                {
                    mol_name: selectedValue
                },
                function(response) {
                    var svg = response.svg
                    $('#svg-container').html(svg)
                }
                )
            }
        )

        $("#button-left").click(
            function()
            {
                $.post("/rotate-left",
                {
                    mol_name: selectedValue
                },
                function(response) {
                    var svg = response.svg
                    $('#svg-container').html(svg)
                }
                )
            }
        )

        $("#button-top").click(
            function()
            {
                $.post("/rotate-up",
                {
                    mol_name: selectedValue
                },
                function(response) {
                    var svg = response.svg
                    $('#svg-container').html(svg)
                }
                )
            }
        )

        $("#button-bottom").click(
            function()
            {
                $.post("/rotate-down",
                {
                    mol_name: selectedValue
                },
                function(response) {
                    var svg = response.svg
                    $('#svg-container').html(svg)
                }
                )
            }
        )
    }
)
