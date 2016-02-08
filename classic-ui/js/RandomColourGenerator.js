function RandomColourGenerator()
{
	this.presetsUsed = 0;
	this.presetColours = [
		'rgb(133,195,41)',
		'rgb(201,4,4)',
		'rgb(36,127,230)',
		'rgb(215, 86, 0)',
		'rgb(255,191,35)',
		'rgb(76,181,245)',
		'rgb(244,204,112)',
		'rgb(222,122,34)',
		'rgb(32,148,139)',
		'rgb(25,149,173)',
		'rgb(245,37,73)',
		'rgb(155,192,28)',
		'rgb(49,169,184)',
		'rgb(249,166,3)',
		'rgb(72,151,216)',
		'rgb(175,68,37)'
	];
	
	this.mappings = {};
}

RandomColourGenerator.prototype.generateColour = function(key)
{
	//If a mapping already exists for the specified key, return it
	if (this.mappings[key] !== undefined) {
		return this.mappings[key];
	}
	
	//Assign the list of presets before generating random values
	if (this.presetsUsed < this.presetColours.length-1)
	{
		this.mappings[key] = this.presetColours[ this.presetsUsed++ ];
		return this.mappings[key];
	}
	
	//Generate a random value
	var r = Math.round(Math.random() * 255);
	var g = Math.round(Math.random() * 255);
	var b = Math.round(Math.random() * 255);
	this.mappings[key] = 'rgb(' + r + ',' + g + ',' + b + ')';
	return this.mappings[key];
}

//Determines whether to use black or white text for the given background colour
//Adapted from the isLight() function in jsColor (<http://jscolor.com/>)
RandomColourGenerator.prototype.isLight = function(colour)
{
	//Split the value into its colour channel components
	var components = colour.replace('rgb(', '').replace(')', '').split(',');
	var r = parseInt(components[0]);
	var g = parseInt(components[1]);
	var b = parseInt(components[2]);
	
	var intensity = (0.213 * r) + (0.715 * g) + (0.072 * b);
	return (intensity >= 255/2);
}
