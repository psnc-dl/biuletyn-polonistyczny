var options = {
    now: "12:00", //hh:mm 24 hour format only, defaults to current time
    twentyFour: true, //Display 24 hour format, defaults to false
    upArrow: 'wickedpicker__controls__control-up', //The up arrow class selector to use, for custom CSS
    downArrow: 'wickedpicker__controls__control-down', //The down arrow class selector to use, for custom CSS
    close: 'wickedpicker__close', //The close class selector to use, for custom CSS
    hoverState: 'hover-state', //The hover state class to use, for custom CSS
    title: '', //The Wickedpicker's title,
    showSeconds: false, //Whether or not to show seconds,
    secondsInterval: 1, //Change interval for seconds, defaults to 1  ,
    minutesInterval: 15, //Change interval for minutes, defaults to 1
    beforeShow: null, //A function to be called before the Wickedpicker is shown
    show: null, //A function to be called when the Wickedpicker is shown
    clearable: true, //Make the picker's input clearable (has clickable "x"),
    timeSeparator: ':'
}

$('.timepicker').wickedpicker(options);