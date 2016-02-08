//Layout algorithm based on the implementation from <https://secure.jcu.edu.au/app/timetable/code.js>

function TimetableRenderer(containerId)
{
	this.containerId = containerId;
	this.colours = new RandomColourGenerator();
	this.daysofweek = 'Monday,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday'.split(',');
	this.times = '7am,730,8am,830,9am,930,10am,1030,11am,1130,12pm,1230,1pm,130,2pm,230,3pm,330,4pm,430,5pm,530,6pm,630,7pm,730,8pm,830,9pm,930'.split(',');
	
	//Populate the default values for the list of blocks
	this.blocks = [];
	for (var i = 0; i < this.daysofweek.length; i++)
	{
		this.blocks.push([]);
		for (var j = 0; j < this.times.length; j++) {
			this.blocks[i].push({startList:[],width:0});
		}
	}
	
	return this;
} 

TimetableRenderer.prototype.render = function()
{
	//Create the table and tbody elements
	var t = document.createElement('table');
	t.setAttribute('class', 'timetable');
	var tb = document.createElement('tbody');
	document.getElementById(this.containerId).appendChild(t);
	t.appendChild(tb);
	
	//Determine the colspan for each day heading
	var maxWidths = [];
	for (var d = 0; d < this.daysofweek.length; d++)
	{
		maxWidths[d] = 1;
		for (var b = 0; b < this.blocks[d].length; b++) {
			maxWidths[d] = Math.max(this.blocks[d][b].width,maxWidths[d]);
		}
	}
	
	//Create the header row and the top-left table cell
	var header = document.createElement('tr');
	tb.appendChild(header);
	var topleft = document.createElement('th');
	topleft.setAttribute('class', 'topleft');
	topleft.appendChild(document.createTextNode('\u00A0'));
	header.appendChild(topleft);
	
	//Create each of the day headings
	for (var day = 0; day < this.blocks.length; day++)
	{
		var c = document.createElement('th');
		c.setAttribute('style', 'width: ' + Math.floor(100 / this.daysofweek.length) + '%');
		var text = document.createTextNode(this.daysofweek[day]);
		c.setAttribute('colspan', maxWidths[day]);
		c.appendChild(text);
		header.appendChild(c);
	}
	
	//Create each table row
	for (var bl = 0; bl < this.blocks[0].length; bl++)
	{
		//Create the table row element
		var r = document.createElement('tr');
		tb.appendChild(r);
		
		//Create the time table cell for the row
		if (bl % 2 == 0)
		{
			var c = document.createElement('td');
			r.appendChild(c);
			c.setAttribute('class', 'time');
			c.setAttribute('rowspan', '2');
			var text = document.createTextNode(this.times[bl]);
			c.appendChild(text);
		}
		
		//Iterate over each of the days
		for (var day = 0; day < this.blocks.length; day++)
		{
			//Create each of the event table cells
			for (var foo = 0; foo < this.blocks[day][bl].startList.length; foo++)
			{
				//Generate a random colour for each subject
				var bgColour = this.colours.generateColour(this.blocks[day][bl].startList[foo].name);
				
				var c = document.createElement('td');
				c.setAttribute('rowspan', this.blocks[day][bl].startList[foo].length);
				c.setAttribute('class', 'event ' + ((this.colours.isLight(bgColour) == true) ? 'light' : 'dark'));
				c.setAttribute('style', 'background-color: ' + bgColour + ';');
				c.innerHTML = this.blocks[day][bl].startList[foo].content;
				r.appendChild(c);
			}
			
			//Create each of the empty table cells
			for (var bar = 0; bar < maxWidths[day] - this.blocks[day][bl].width; bar++)
			{
				var c = document.createElement('td');
				var text = document.createTextNode('\u00A0');
				r.appendChild(c);
				c.appendChild(text);
			}
		}
	}
}

TimetableRenderer.prototype.addEvent = function(day, startBlock, lengthInBlocks, key, text)
{
	this.blocks[day][startBlock].startList.push({content:text,length:lengthInBlocks,name:key});
	for (var i = startBlock; i < startBlock + lengthInBlocks; i++) {
		this.blocks[day][i].width++;
	}
}
