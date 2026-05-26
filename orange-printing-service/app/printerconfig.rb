# frozen_string_literal: true

require "sinatra/base"
require "sinatra/cookies"
require "socket"
require "timeout"

class PrinterConfig < Sinatra::Base
  helpers Sinatra::Cookies

  set :root, File.dirname(__FILE__)
  set :views, File.expand_path("views", __dir__)
  set :public_folder, File.expand_path("public", __dir__)

  set :static, true
  set :show_exceptions, false
  set :raise_errors, false
  set :host_authorization, { permitted_hosts: [] }

  ADMIN_USER = "admin"
  ADMIN_PASS = "Orange_is_the_new_Black123"

  def logged_in?
    request.cookies["orange_admin"] == "true"
  end

  def failed_login
    redirect "/#failed_login", 302
  end

  get "/" do
    erb :login
  end

  get "/printerconfig.rb" do
    content_type "text/plain"

    <<~RUBY_SOURCE
      # frozen_string_literal: true

      require "sinatra/base"
      require "sinatra/cookies"
      require "socket"
      require "timeout"

      class PrinterConfig < Sinatra::Base
        helpers Sinatra::Cookies

        ADMIN_USER = "admin"
        ADMIN_PASS = "Orange_is_the_new_Black123"

        def logged_in?
          request.cookies["orange_admin"] == "true"
        end

        def failed_login
          redirect "/#failed_login", 302
        end

        post "/login" do
          failed_login unless params[:username] == ADMIN_USER
          failed_login unless params[:password] == ADMIN_PASS

          response.set_cookie(
            "orange_admin",
            value: "true",
            path: "/",
            httponly: true,
            same_site: :strict
          )

          redirect "/settings", 302
        end

        post "/test-connection" do
          failed_login unless logged_in?

          output = ""
          c = params[:ipaddress].split(":")

          raise "The reception printer only supports local diagnostics." unless c[0] == "127.0.0.1"

          Socket.tcp(c[0], c[1].to_i, connect_timeout: 1) do |sock|
            sock.puts params[:testcommand]

            Timeout.timeout(3) do
              while line = sock.read(1)
                output += line
              end
            end

            sock.close
          end

          output
        rescue Errno::ECONNRESET
          output
        rescue Exception => e
          "Output: \#{output}\\nError: \#{e}"
        end
      end
    RUBY_SOURCE
  end

  post "/login" do
    failed_login unless params.key?(:username)
    failed_login unless params.key?(:password)

    failed_login unless params[:username] == ADMIN_USER
    failed_login unless params[:password] == ADMIN_PASS

    response.set_cookie(
      "orange_admin",
      value: "true",
      path: "/",
      httponly: true,
      same_site: :strict
    )

    redirect "/settings", 302
  end

  get "/logout" do
    response.delete_cookie("orange_admin", path: "/")
    redirect "/", 302
  end

  get "/settings" do
    failed_login unless logged_in?

    erb :settings
  end

  post "/test-connection" do
    failed_login unless logged_in?

    output = ""

    ipaddress = params[:ipaddress].to_s.strip
    testcommand = params[:testcommand].to_s

    halt 400, "Missing printer diagnostic target." if ipaddress.empty?
    halt 400, "Missing diagnostic command." if testcommand.empty?

    c = ipaddress.split(":")

    raise "Hosts other than 127.0.0.1 are blocked by Orange Plant policy." unless c[0] == "127.0.0.1"
    raise "Port is missing." unless c.length == 2
    raise "Invalid port." unless c[1].match?(/\A[0-9]{1,5}\z/)

    port = c[1].to_i
    raise "Invalid port range." unless port.between?(1, 65_535)

    Socket.tcp(c[0], port, connect_timeout: 1) do |sock|
      sock.puts testcommand

      Timeout.timeout(3) do
        while (char = sock.read(1))
          output += char
        end
      end

      sock.close
    end

    content_type "text/plain"
    output
  rescue Errno::ECONNREFUSED
    content_type "text/plain"
    "Output: #{output}\nError: Connection refused by local diagnostic service."
  rescue Errno::ECONNRESET
    content_type "text/plain"
    output
  rescue Timeout::Error
    content_type "text/plain"
    "Output: #{output}\nError: Local diagnostic service timed out."
  rescue Exception => e
    content_type "text/plain"
    "Output: #{output}\nError: #{e}"
  end

  not_found do
    status 404
    erb :error404
  end

  error do
    status 500
    erb :error404
  end
end
