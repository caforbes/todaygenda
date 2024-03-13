# frozen_string_literal: true

require 'rake'
require 'rake/testtask'
require 'rubocop/rake_task'

# Define tasks
desc 'Run the main task (lint, tests)'
# desc 'Run the main task (tests, testdb teardown, lint)'
task default: [:precommit]

desc 'Run linter and tests'
task precommit: %i[lint test]

desc 'Run tests'
Rake::TestTask.new(:test) do |t|
  t.libs << 'test'
  t.test_files = FileList['test/*_test.rb']
end

desc 'Run Rubocop linter and fix simple issues'
RuboCop::RakeTask.new(:lint) do |task|
  task.requires << 'rubocop-rake'
  task.options = ['--autocorrect']
end

desc 'Run Rubocop linter and fix all correctable issues'
RuboCop::RakeTask.new(:hardlint) do |task|
  task.requires << 'rubocop-rake'
  task.options = ['--autocorrect-all']
end
