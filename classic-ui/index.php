<?php

//Determines if a string exists within another string
function instr($needle, $haystack)
{
	//Function to test if a string exists inside another string (case insensitive)
	$pos = strpos(strtolower($haystack), strtolower($needle));
	if ($pos === false) { return false; } else { return true; }
}

//Generates a dropdown based on a list of valid options, and a selected value
function generateDropdown($name, $values, $selected)
{
	$dropdown = '<select name="' . htmlentities($name) . '">';
	foreach ($values as $value => $label) {
		$dropdown .= '<option value="' . htmlentities($value) . '"' . ($value == $selected ? ' selected="selected"' : '') . '>' . htmlentities($label) . '</option>';
	}
	
	$dropdown .= '</select>';
	return $dropdown;
}

//Strips extra characters from the subject list that people might use as delimiters
function strip_delims($s)
{
	$s = str_replace(',', ' ', $s);
	$s = str_replace(';', ' ', $s);
	while (instr('  ', $s) === true) {
		$s = str_replace('  ', ' ', $s);
	}
	
	return trim($s);
}

//The list of valid days of the week
$days = Array(
	'Monday',
	'Tuesday',
	'Wednesday',
	'Thursday',
	'Friday',
	'Saturday',
	'Sunday'
);

//The list of valid campuses
$campuses = Array(
	'CBH' => 'Cairns Base Hospital',
	'CCC' => 'Cairns City',
	'CNJ' => 'Cloncurry',
	'CNS' => 'Cairns Smithfield',
	'ISA' => 'Mount Isa',
	'MKY' => 'Mackay',
	'TCC' => 'Townsville City',
	'TIS' => 'Thursday Island',
	'TMH' => 'Townsville Mater Hospital',
	'TSV' => 'Townsville Douglas',
	'TTH' => 'The Townsville Hospital'
);

//The list of valid study periods
$studyPeriods = Array(
	'1'  => 'SP1',
	'2'  => 'SP2',
	'3'  => 'SP3',
	'4'  => 'SP4',
	'5'  => 'SP5',
	'6'  => 'SP6',
	'7'  => 'SP7',
	'8'  => 'SP8',
	'9'  => 'SP9',
	'10' => 'SP10',
	'11' => 'SP11'
);

//Determine default year and study period settings
$currYear = date('Y');
$currSem  = ((int)date('n') <= 6) ? 'sp1' : 'sp2';

//Retrieve the arguments and supply our default values if needed
$semester = (!empty($_REQUEST['sp']))       ? $_REQUEST['sp']                     : $currSem;
$campus   = (!empty($_REQUEST['campus']))   ? $_REQUEST['campus']                 : 'CNS';
$subjects = (!empty($_REQUEST['subjects'])) ? strip_delims($_REQUEST['subjects']) : '';

//Perform the scrape of the source timetable
$events = Array();
if (!empty($subjects)) {
	$events = json_decode(file_get_contents('http://127.0.0.1:5000/timetable?subjects=' . urlencode($subjects) . '&campus=' . urlencode($campus) . '&sp=' . urlencode($semester)), true);
}

?>
<!doctype html>
<html>
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
		
		<title>JCU 2016 Timetable - "Classic" Interface</title>
		
		<link rel="stylesheet" type="text/css" href="./css/styles.css">
		<script type="text/javascript" src="./js/jquery-2.2.0.min.js"></script>
		<script type="text/javascript" src="./js/RandomColourGenerator.js"></script>
		<script type="text/javascript" src="./js/TimetableRenderer.js"></script>
	</head>
	<body>
		<div id="controls">
			<h1>JCU 2016 Timetable - "Classic" Interface</h1>
			<p class="instructions">Separate subject codes with spaces. Wildcards and partial matching supported.<br>(Examples: "cp1" for all first-year IT subjects, "cp1*4" for first-year IT subjects whose subject code ends in the number 4.)</p>
			<form action="<?php echo $_SERVER['PHP_SELF']; ?>" method="get">
				<table>
					<tbody>
						<tr><td>Campus:</td><td><?php echo generateDropdown('campus', $campuses, $campus); ?></td></tr>
						<tr><td>Study Period:</td><td><?php echo generateDropdown('sp', $studyPeriods, $semester); ?></td></tr>
						<tr><td>Subjects:</td><td><input type="text" name="subjects" id="subjects" value="<?php echo htmlentities($subjects); ?>"></td></tr>
						<tr><td colspan="2" class="submit"><input type="submit" value="Display Timetable"></td></tr>
					</tbody>
				</table>
			</form>
		</div>
		<div id="ttdiv"></div>
		<script type="text/javascript">
			var tt = new TimetableRenderer('ttdiv');
			
			<?php
				foreach ($events as $event)
				{
					//Determine the day, start time, and end time offsets
					$day   = array_search($event['day'], $days);
					$start = ((strtotime($event['start']) - strtotime('7:00am')) / 60 / 30);
					$end   = ((strtotime($event['end']) - strtotime($event['start'])) / 60 / 30);
					
					# Extract the subject code from the activity name and generate the StudyFinder link
					$pos = strpos($event['activity'], '_');
					$subject = substr($event['activity'], 0, $pos);
					$link = 'https://secure.jcu.edu.au/app/studyfinder/?subject=' . $subject;
					
					# Extract the subject identifier (subject code + campus + SP) from the activity name
					$identifier = $event['activity'];
					$find = strtoupper($semester) . '_';
					$pos = strpos($event['activity'], $find);
					if ($pos !== false) {
						$identifier = substr($event['activity'], 0, $pos + strlen($find));
					}
					
					//If Cairns Smithfield or Townsville Douglas is the selected campus, link the room to the interactive map
					$campus = strtoupper($campus);
					$roomMarkup = htmlentities($event['rooms']);
					if ($campus == 'CNS' || $campus == 'TSV')
					{
						$roomLink = 'https://maps.jcu.edu.au/campus/' . (($campus == 'CNS') ? 'cairns' : 'townsville') . '/?location=' . urlencode($event['rooms']);
						$roomMarkup = '<a href=\\"' . $roomLink . '\\">' . $roomMarkup . '</a>';
					}
					
					//Generate the HTML for the table cell
					$markup  = '<strong><a href=\\"' . htmlentities($link) . '\\">' . htmlentities(str_replace('_' . $event['type'], ' ' . $event['type'], $event['activity'])) . '</a></strong><br>';
					if (!instr($event['type'], $event['activity'])) {
						$markup .= htmlentities($event['type']) . '<br>';
					}
					$markup .= $roomMarkup . '<br>';
					$markup .= htmlentities(implode(' ', array_reverse(explode(', ', $event['staff']))));
					
					//Output the addEvent() call
					echo 'tt.addEvent(' . $day . ',' . $start . ',' . $end . ',"' . htmlentities($identifier) . '","' . $markup . '");';
				}
				
				if (count($events) > 0) {
					echo 'tt.render();';
				}
			?>
		</script>
	</body>
</html>