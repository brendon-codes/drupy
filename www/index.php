<?php
	if (strcasecmp($_SERVER['SERVER_NAME'], 'drupy.net') !== 0):
		header( "HTTP/1.1 301 Moved Permanently" );
		header( "Location: http://drupy.net" );
	endif;
	print "<" . "?xml version='1.0' encoding='UTF-8'?" . ">\n";
?>
<!DOCTYPE html
	PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
	"DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
	<head>
		<title>Drupy: Drupal in Python</title>
		<meta name="revised" content="Drupy, 06/27/2008" />
		<meta name="verify-v1" content="jEk8c88dgEev9x3hfBbvxz3n0pqB+LtEM0PHhK4nYxo=" />
		<style type="text/css" media="screen">
			p
			{
				font-size : 85%;
			}
			body
			{
				text-align : center;
			}
			body,
			body td
			{
				font-family : Lucida Grande, Geneva, Arial, Verdana, sans-serif;
				color : #333;
			}
			#main
			{
				margin : 5% auto 20% auto;
				width : 50%;
				text-align : left;
			}
			h1
			{
				color : #933;
				margin : 0%;
			}
			h2
			{
				color : #999;
				margin : 0% 0% 0% 2%;
			}
			h3
			{
			  margin : 0px;
			}
			a
			{
				color : #933;
			}
			.status-title
			{
			  color : #F00;
			  font-size : 70%;
			  font-weight : normal;
			  margin : 0px;
			}
		</style>
	</head>
	<body>
		<div id="main">
			<h1>Drupy</h1>
			<h2>Drupal&#8230; in Python</h2>
			<p class="status-title">
			  Updated 06/27/2008
			</p>
			<p>
				Drupy is a Python port of the <a href="http://drupal.org/" title="Drupal: Community Plumbing">Drupal</a> content management system, which until now was only available in PHP.
			</p>
			<p>
				Drupy is not yet production-ready, but the Drupy developers are working hard to put out a stable release. Python developers are strongly encouraged to contribute.
			</p>
			<h3>Contacting Us</h3>
			<p>
				The Drupy developers can be contacted through the <a href="http://sourceforge.net/projects/drupy" title="Drupy: Drupal in Python">Drupy Sourceforge page</a>. The Drupy project can also be found on irc at <a href="irc://freenode.net/#drupy">Freenode.net&#47;&#35;drupy</a>
			</p>
			<h3>Getting the Code</h3>
			<p>
				The latest Drupy codebase is available via GIT at <a href="http://gitorious.org/projects/drupy/repos/mainline">Gitorious</a>.
			</p>
			<h3>API Documentation</h3>
			<p>
				If you want to see whats under the hood, have a look at the <a href='/docs/'>Drupy API Documentation</a>.
			</p>
			<h3>Current Status</h3>
			<p>
				Currently, Drupy can load core modules/plugins and execute the core init hook. The core system plugin (Drupal's system.module) is almost complete. For more details, check the <a href="/status/">Drupy diagnostic page</a>, which is updated regularily.
			</p>
			<h3>Special Thanks</h3>
			<p>
				The name "Drupy" was kindly transferred to us by <a href='http://kzo.net/'>Keizo Gates</a>. Keizo Gates is not affiliated with the Drupy project, so please do not contact him with Drupy questions.
			</p>
		</div>
		<script type="text/javascript">
			var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
			document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));
		</script>
		<script type="text/javascript">
			var pageTracker = _gat._getTracker("UA-4793451-1");
			pageTracker._initData();
			pageTracker._trackPageview();
		</script>
	</body>
</html>
