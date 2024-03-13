# frozen_string_literal: true

require_relative 'todaygenda'

##
# Represents the command line application.
class CLIApp
  def initialize
    @list = DayList.new
  end

  def hello
    display_welcome
    loop do
      display_list
      prompt_next_action
      choice = gets.chomp.upcase
      continue = process_choice!(choice)
      break unless continue

      clear_screen
    end
  end

  private

  def clear_screen
    system('clear') || system('cls')
  end

  def available_actions
    {
      add: { code: 'N', prompt: 'Add a new task' },
      close: { code: 'X', prompt: 'Close' }
    }
  end

  def display_welcome
    puts "Welcome to Todaygenda! Let's get started."
  end

  def display_list
    if @list
      puts ''
      puts @list
      puts ''
    else
      puts 'You have no tasks in your list yet.'
    end
  end

  def display_actions
    available_actions.each_value do |object|
      puts "(#{object[:code]}) #{object[:prompt]}"
    end
  end

  def prompt_next_action
    puts 'What do you want to do?'
    display_actions
  end

  def process_choice!(choice)
    available_options = available_actions.transform_values { |obj| obj[:code] }.invert
    action = available_options[choice]
    case action
    when :close
      false
    else
      true
    end
  end
end

CLIApp.new.hello
