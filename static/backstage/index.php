<?

#if (!isset($_COOKIE['godot']) || $_COOKIE['godot'] != md5('tiaomiwym123')) {
#        header('Location: /');
#        exit;
#}

?>
<html>
    <head>
        <title>Theatricalia</title>
        <style type="text/css">
            body {
                font-family: Optima, "Zapf Humanist", "MgOpen Cosmetica", Candara, Myriad, "Lucida Grande", "Lucida Sans Unicode", "Lucida Sans", Frutiger, "Trebuchet MS", sans-serif;
                margin: 1.5em;
                padding: 0;
                text-align: center;
            }
            img { cursor: pointer; }
        </style>
        <script type="text/javascript">
            var current = 2;
            function prev() {
                document.getElementById('ss'+current).style.display = 'none';
                current = current - 1;
                if (current < 2) current = 7;
                document.getElementById('ss'+current).style.display = 'inline';
            }
            function next() {
                document.getElementById('ss'+current).style.display = 'none';
                current = current + 1;
                if (current > 7) current = 2;
                document.getElementById('ss'+current).style.display = 'inline';
            }
        </script>
    </head>
    <body><!-- Flung together, normal coding style much better :) -->

        <p> Current development level screenshots. <a href="#" onclick="next(); return false">Next</a> |
        <a href="#" onclick="prev(); return false">Previous</a>. <a href="/">Live site</a></p>

<p>
<!-- <img id="ss1" src="PlaysH.png" onclick="next(1); return false;"> -->
<img id="ss2" src="Courtyard.png" onclick="next(); return false;" height="636">
<img id="ss3" src="HamletRSC.png" style="display:none" onclick="next(); return false;" height="636">
<img id="ss4" src="Tennant.png" style="display:none" onclick="next(); return false;" height="636">
<img id="ss5" src="Hamlet.png" style="display:none" onclick="next(); return false;" height="636">
<img id="ss6" src="PeopleT.png" style="display:none" onclick="next(); return false;" height="636">
<img id="ss7" src="Edit1.png" style="display:none" onclick="next(); return false;" height="636">
</p>

</body>
</html>
