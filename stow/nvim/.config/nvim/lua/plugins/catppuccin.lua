return {
  {
    "catppuccin/nvim",
    lazy = false,
    name = "catppuccin",
    priority = 1000,

    config = function()
      require("catppuccin").setup({
        transparent_background = false,
        color_overrides = {
          mocha = {
            base = "#1e1d1c",
          },
        },
      })
      vim.cmd.colorscheme("catppuccin-mocha")
    end,
  },
}
