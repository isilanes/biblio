module.exports = {
  content: [
    '../../templates/**/*.html',
    '../../../**/templates/**/*.html',
    '../../../**/*.py',
  ],
  safelist: [
    'peer',
    'peer-checked:bg-blue-600',
    'peer-checked:text-white',
    'bg-gray-100',
    'text-gray-700',
    'border',
    'border-gray-300',
    'rounded-lg',
    'px-4',
    'py-2',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
