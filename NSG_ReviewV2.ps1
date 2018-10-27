#
# Usage:
#
# Open this in PowerShell ISE and click the Run button. That's it!
# Once finished, the script will write a .csv file into the working directory
# 
# There are multiple sets of data which are stored but not written to disk:
#
# $dtresults - abbreviated version of what is written to .csv
# $artHash - hash table of all artifacts found
# $catHash - hash table of all categories found
# $portHash - hast table of all ports; does not include port ranges like '137-139'
#
# Note: It's normal for the script to throw a ton of errors; this is because not all JSON files
#       contain the objects we're looking for. Be patient, it WILL complete.
#
# Additional endpoints are below; unsure if they're reachable via normal methods
#
# https://gallery.azure.com/";
# https://gallery.chinacloudapi.cn/";
# https://gallery.usgovcloudapi.net/";
# https://gallery.cloudapi.de/";

$a = Invoke-WebRequest -Uri "https://gallery.azure.com/Microsoft.Gallery/galleryitems?api-version=2015-10-01&includePreview=true" |ConvertFrom-Json

# Zero variables
$v = ""
$creds= "False"
$count = 0

# Get today's date and instantiate hash tables
$today = Get-Date -Format d

$imageList = @{}
$imagePub = @{}
$imageDesc = @{}
$dtList = @{}
$dtPub = @{}
$dtDesc = @{}
$changedTime = @{}
$createdTime = @{}
$porthash = @{}
$catHash = @{}
$artHash = @{}

# Add category tags to category hash table
foreach($identity in $a) {
    foreach($category in $identity.categoryIds) {
    $catHash[$category]++
    }
}

# Add artifacts to artifact hash table
foreach($identity in $a) {
    foreach($name in $identity.artifacts.name) {
    $artHash[$name]++
    }
}

foreach($identity in $a) {
    foreach($artifact in $identity.artifacts) {
    if ($artifact.name.Equals("createuidefinition")){
        $imageList.Add($identity.itemName,$artifact.uri)
        $imagePub.Add($identity.itemName,$identity.publisher)
        $imageDesc.Add($identity.itemName,$identity.description)
        $changedTime.Add($identity.itemName,$identity.changedTime)
        $createdTime.Add($identity.itemName,$identity.createdTime)
    }
    if ($artifact.name.Equals("DefaultTemplate")){
        $dtList.Add($identity.itemName,$artifact.uri)
        $dtPub.Add($identity.itemName,$identity.publisher)
        #$dtDesc.Add($identity.itemName,$identity.description)
        }
    }
}

$results = @()
$dtResults = @()
$portstats = @()
$results += "Created On,Vendor,Num. Exposed Ports,Image Name,Credentials,Changed,Image Age,Open Ports"
$dtResults += "Vendor,Num. Exposed Ports,Image Name,Open Ports"
$portstats += "Vendor,Image Name,Open Ports"
foreach($key in $imageList.Keys)
{
    $url = $imageList[$key]
    $vendor = $imagePub[$key]
    $desc = $imageDesc[$key]
    $changed = $changedTime[$key] |Get-Date -Format d
    $created = $createdTime[$key] |Get-Date -Format d
    
    # Do math to find the delta between image creation & last update

    $c1 = [DateTime] $today
    $c2 = [DateTime] $changed
    $delta = ($c1 - $c2).TotalDays

    $b = Invoke-WebRequest -Uri $url | ConvertFrom-Json
    if($desc.Contains("Username")) {
        if($desc.Contains("Password")) {
            $creds = "True"
            }
    }
    $count = $b.parameters.networkSecurityGroupRules.Count
    if ($count -ne '0') {
        foreach ($port in $b.parameters.networkSecurityGroupRules.destinationPortRange |Sort-Object) {
            $port | %{$v += ($(if($v){","}) + $_)}
            $porthash[$port]++
        }
    } 
    $results += "$($created),$($vendor),$($count),$($key),$($creds),$($changed),$($delta),$($v)"
    $portstats += "$($vendor),$($key),$($v)"
    $v = ""
    $creds= "False"
    $count = 0
}

foreach($key in $dtList.Keys)
{
    $url = $dtList[$key]
    $vendor = $dtPub[$key]

    $dt = Invoke-WebRequest -Uri $url | ConvertFrom-Json

    $count = $dt.resources.properties.securityRules.properties.destinationPortRange.Count
    if ($count -ne '0') {
        foreach ($port in $dt.resources.properties.securityRules.properties.destinationPortRange |Sort-Object) {
            $port | %{$dtv += ($(if($dtv){","}) + $_)}
                #if (-not ($ports -contains $port)){
                #    $ports += $port
                #}
            #$porthash[$port]++
        }
    $dtResults += "$($vendor),$($count),$($key),$($dtv)"
    #$portstats += "$($vendor),$($key),$($v)"
    $dtv = ""
    $count = 0
    } 
}

$daytime = "{0:yyyyMMddHHmm}" -f (get-date)
$filenamecsv = "AMP_NSG_Report_" + $daytime + ".csv"
$results |out-file $filenamecsv -Encoding ascii
#$porthash.GetEnumerator() |Sort -Property value
#$catHash.GetEnumerator() |Sort -Property value
#$artHash.GetEnumerator() |Sort -Property value