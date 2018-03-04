<?xml version='1.0'?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
        <rdf:RDF
			xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" 
			xmlns:MAWSList="http://Bradley.ac.uk/MAWS/Assignment/DeviceList#"
			xmlns:MAWSDevice="http://Bradley.ac.uk/MAWS/Assignment/DeviceList/Device#"
			xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#" 
			xmlns:owl="http://www.w3.org/2002/07/owl#">
        <rdf:Description rdf:about="http://Bradley.ac.uk/MAWS/Assignment/DeviceList">
        	<xsl:for-each select="DeviceList/Device">
            <MAWSList:hasDevice>
	            <rdf:Description rdf:about="http://Bradley.ac.uk/MAWS/Assignment/DeviceList/Device">  
		            <MAWSDevice:hasID>
		                <xsl:value-of select="id"/>
		            </MAWSDevice:hasID>

		            <MAWSDevice:hasName>
		                <xsl:value-of select="name"/>
		            </MAWSDevice:hasName>

		            <MAWSDevice:hasLocation>
		                <xsl:value-of select="location"/>
		            </MAWSDevice:hasLocation>

		            <MAWSDevice:hasType>
		                <xsl:value-of select="type"/>
		            </MAWSDevice:hasType>

		            <MAWSDevice:hasValue>
		                <xsl:value-of select="value"/>
		            </MAWSDevice:hasValue>		        
		        </rdf:Description>
	    	</MAWSList:hasDevice>
	    	</xsl:for-each>
      	</rdf:Description>
    	</rdf:RDF>
    </xsl:template>
</xsl:stylesheet>
       