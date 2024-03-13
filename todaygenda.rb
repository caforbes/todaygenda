# frozen_string_literal: true

##
# Represents the tasks and events to manage today.
# TODO: add new method docs
class DayList
  def initialize
    @tasks = []
  end

  def to_s
    string = "Today's list: "
    if empty?
      string += "\n(no tasks yet)"
    else
      @tasks.each { |task| string += "\n#{task}" }
    end
    string
  end

  # :section: Reading
  # methods relating to reading the list
  
  def empty?
    @tasks.empty?
  end

  def all_done?
    !empty? and @tasks.all?(&:complete?)
  end

  def next
    @tasks.select(&:pending?).first
  end
  
  # :section: Writing
  # methods relating to updating the list
  
  def add_task(name)
    task = Task.new(name)
    @tasks.push(task)
  end
end

##
# Represents a single task for completion.
# TODO: add method docs
class Task
  attr_accessor :name

  # @return [Symbol] the task status, one of :new, :active, :done
  attr_reader :status

  TASK_STATUSES = {
    new: { prefix: '  ' },
    active: { prefix: '> ' },
    done: { prefix: 'X ' }
  }.freeze

  # @param  name [String] the name of the task
  def initialize(name)
    @name = name
    @status = :new
  end

  def to_s
    TASK_STATUSES[status][:prefix] + name
  end

  # :section: Reading
  # methods relating to reading the task or its properties
  
  def complete?
    @status == :done
  end

  def active?
    @status == :active
  end

  def pending?
    @status == :new
  end

  # :section: Writing
  # methods relating to updating the task or its properties
  
  # Mark the task as done
  def complete!
    @status = :done
  end

end
