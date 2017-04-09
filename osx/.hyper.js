module.exports = {
  config: {
    // default font size in pixels for all tabs
    fontSize: 14,

    // font family with optional fallbacks
    fontFamily: 'Menlo, "DejaVu Sans Mono", "Lucida Console", monospace',

    // terminal cursor background color and opacity (hex, rgb, hsl, hsv, hwb or cmyk)
    // cursorColor: 'rgba(248,28,229,0.75)',
    cursorColor: 'rgba(255,255,255,0.50)',

    // `BEAM` for |, `UNDERLINE` for _, `BLOCK` for █
    cursorShape: 'BEAM',

    // color of the text
    foregroundColor: '#eee',

    // terminal background color
    backgroundColor: '#222',

    // border color (window, tabs)
    borderColor: '#333',

    // custom css to embed in the main window
    css: '',

    // custom css to embed in the terminal window
    termCSS: '',

    // custom padding (css format, i.e.: `top right bottom left`)
    padding: '0px 0px 18px 0px',

    // window size
    windowSize: [800, 600],

    // the full list. if you're going to provide the full color palette,
    // including the 6 x 6 color cubes and the grayscale map, just provide
    // an array here instead of a color map object

    // iTerm2 Colors:
    colors: {
      black: '#626262',
      red: '#ff8373',
      green: '#b4fb73',
      yellow: '#fffdc3',
      blue: '#a5d5fe',
      magenta: '#ff90fe',
      cyan: '#d1d1fe',
      white: '#f1f1f1',
      lightBlack: '#8f8f8f',
      lightRed: '#ffc4be',
      lightGreen: '#d6fcba',
      lightYellow: '#fffed5',
      lightBlue: '#c2e3ff',
      lightMagenta: '#cc00ff',
      lightCyan: '#ffb2fe',
      lightWhite: '#ffffff'
    },

    // the shell to run when spawning a new session (i.e. /usr/local/bin/fish)
    // if left empty, your system's login shell will be used by default
    shell: '/usr/local/bin/zsh'

    // for advanced config flags please refer to https://hyperterm.org/#cfg
  },

  // a list of plugins to fetch and install from npm
  // format: [@org/]project[#version]
  // examples:
  //   `hyperpower`
  //   `@company/project`
  //   `project#1.0.1`
  plugins: [
    //'hyperpower',
    'hypercwd',
    //'hypercolors',
    //'hyperterm-snazzy',
    //'hyperterm-base16-ocean-saturated',
    //'hyperterm-tabs',
    //'hyperterm-oceanic-next'
    //'hyper-oceans16'
    //'hyper-chesterish'
    //'hyper-snazzy'
    //'hyper-now'
    //'hyper-simple-vibrancy',
    'hyperterm-cursor',
    //'hyperline',
    'hyper-statusline',
    'hyper-tabs-enhanced'
  ],

  hyperStatusLine: {
    fontSize: 14,
  },

  // in development, you can create a directory under
  // `~/.hyperterm_plugins/local/` and include it here
  // to load it and avoid it being `npm install`ed
  localPlugins: []
};
