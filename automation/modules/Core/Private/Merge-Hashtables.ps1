function Merge-Hashtables {
    <#
    .SYNOPSIS
        Merges two or more hashtables into a single hashtable.
    
    .DESCRIPTION
        This function takes multiple hashtables and merges them into a single hashtable.
        In case of key conflicts, the value from the rightmost hashtable takes precedence.
        Nested hashtables are merged recursively.
    
    .PARAMETER Source
        One or more hashtables to merge.
    
    .EXAMPLE
        $defaults = @{ A = 1; B = @{ X = 10; Y = 20 } }
        $overrides = @{ B = @{ Y = 200; Z = 30 }; C = 3 }
        $merged = Merge-Hashtables $defaults, $overrides
        # Result: @{ A = 1; B = @{ X = 10; Y = 200; Z = 30 }; C = 3 }
    #>
    [CmdletBinding()]
    [OutputType([hashtable])]
    param(
        [Parameter(Mandatory = $true, ValueFromPipeline = $true)]
        [AllowEmptyCollection()]
        [hashtable[]]$Source
    )
    
    $result = @{}
    
    foreach ($hashtable in $Source) {
        if ($null -eq $hashtable) { continue }
        
        foreach ($key in $hashtable.Keys) {
            $sourceValue = $hashtable[$key]
            $targetValue = $result[$key]
            
            # If both values are hashtables, merge them recursively
            if ($null -ne $targetValue -and $targetValue -is [hashtable] -and $sourceValue -is [hashtable]) {
                $result[$key] = Merge-Hashtables -Source $targetValue, $sourceValue
            } else {
                # Otherwise, the rightmost value takes precedence
                $result[$key] = $sourceValue
            }
        }
    }
    
    return $result
}
