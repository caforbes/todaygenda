# frozen_string_literal: true

require 'simplecov'
require 'simplecov-console'

SimpleCov.start do
  enable_coverage :branch
end
SimpleCov.formatter = SimpleCov::Formatter::MultiFormatter.new(
  [SimpleCov::Formatter::HTMLFormatter, SimpleCov::Formatter::Console]
)
SimpleCov::Formatter::Console.missing_len = 20

require 'minitest/autorun'
require 'minitest/reporters'
Minitest::Reporters.use!

require_relative '../todaygenda'

class DayListTest < Minitest::Test
  def setup
    @daylist = DayList.new
    # TODO: factory for todo 1, todo 2, iterator
  end

  def test_add_task
    setup
    @daylist.add_task('task 1')
    assert_equal('task 1', @daylist.next.name)
  end
end
