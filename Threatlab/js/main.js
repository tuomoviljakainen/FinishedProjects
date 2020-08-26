class Intel extends React.Component {
    constructor(props) {
        super(props);
        this.state = {totalvirus: {}, urlscan: {}, urlscanState: "", urlscanScanResultPage: {}, abuseipdb: {}, dataType: ""};
        this.getResults = this.getResults.bind(this);
        this.virustotalApiCall = this.virustotalApiCall.bind(this);
        this.virusTotalBuild = this.virusTotalBuild.bind(this);
		this.addIPhostnameResolutions = this.addIPhostnameResolutions.bind(this);
		this.handleUrlScanData = this.handleUrlScanData.bind(this);
		this.setScanID = this.setScanID.bind(this);
		this.urlscanBuild = this.urlscanBuild.bind(this);
		this.abuseipdbApiCall = this.abuseipdbApiCall.bind(this);
		this.abuseipdbBuild = this.abuseipdbBuild.bind(this);
		this.abuseipdbReports = this.abuseipdbReports.bind(this);
        this.virustotalAVresults = this.virustotalAVresults.bind(this);
    }
    
	// Jos käyttäjä on vaihtanut sivua vierailtuaan Intel-sivulla ja tulee takaisin
	// Intel-sivulle, sivu renderöidään samanlaiseksi ennen kuin käyttäjä vaihtoi sivua	
    componentDidMount() {
        
		// Muuttujat joihin data ylemmistä komponenteista tallennetaan
        this._isMounted = true;  
        var virustotalResults = {};
        var urlscanResults = {};
        var urlscanState = "";
        var abuseipdbResults = {};
        var dataType = "";
        this.refs.intelSearch.value = this.props.intelSearch;
        
		// Katsotaan onko PageSelect komponentin dataType-objektiin varastoity datatyyppiä
		// Jos on tallennetaan sen arvo dataType muuttujalle
        if (this.props.dataType != 0) {
            dataType = this.props.dataType;
        }
        
		// Katsotaan onko PageSelect komponentin abuseipdb-objekti tyhjä
		// Jos ei ole tallennetaan sen arvo abuseipdbResults muuttujalle
        if (!(jQuery.isEmptyObject(this.props.abuseipdb))) {
            abuseipdbResults = this.props.abuseipdb;
        }
		
		// Jos PageSelect komponentin urlscan-objekti ei ole tyhjä ja urlscanState-objekti sisältää merkkijonon "done"
		// Tallennetaan arvot muuttujiin
		if (this.props.urlscan.length != 0 && this.props.urlscanState == "done") {
            urlscanResults = this.props.urlscan;
            urlscanState = "done";
        }
		
		// Jos PageSelect komponentin urlscanState-objekti sisältää merkkijonon "waiting" ja urlscanScanResultPage ei ole tyhjä
		// urlscanin APIn tulosten lataaminen on jäänyt aiemmin kesken ja nyt se voidaan aloittaa uudelleen
        else if (this.props.urlscanState == "waiting" && (!(jQuery.isEmptyObject(this.props.urlscanScanResultPage)))) {
            urlscanState = "waiting";
            $.when(this.setScanID(this.props.urlscanScanResultPage, true)).done(setTimeout(this.handleUrlScanData, 45000));
        }
        
		// Jos PageSelect komponentin virustotal-objekti ei ole tyhjä
		// Tallennetaan sen arvo muuttujaan virustotalResults
        if (!(jQuery.isEmptyObject(this.props.virustotal))) {
            virustotalResults = this.props.virustotal;
        }
        
		// Lopuksi tallennetaan tulokset Intel-objektin vastaaviin state-objekteihin ja renderöidään sivu uudelleen setState:n avulla
        this.setState({totalvirus: virustotalResults, abuseipdb: abuseipdbResults, urlscan: urlscanResults, dataType: dataType, urlscanState: urlscanState})
    }
    
    // Tallennetaan kaikki merkitykselliset tulokset ylempään PageSelect komponenttiin Intel-komponentin tuhoutuessa
    componentWillUnmount () {
        this.props.saveIntelResults(this.state.totalvirus, this.state.abuseipdb, this.state.urlscan, this.refs.intelSearch.value, this.state.dataType, this.state.urlscanState, this.state.urlscanScanResultPage);
    }
	
	    //2d75cc1bf8e57872781f9cd04a529256
        //chrome.exe --user-data-dir="C:/Chrome dev session" --disable-web-security
    
	// Kutsutaan VirusTotalin APIa
    virustotalApiCall (resource, dataType) {
               
        let url;
        let apiKey = "50881f506e18977d81ff47a24b276d2f3065189e02316a3611c9c0c9e2d8115e";
        let resourceType = "";
        
        // API kutsu riippuu pyydettävän datan tyypistä
        if (dataType == "IPaddress") {
            url = `https://www.virustotal.com/vtapi/v2/ip-address/report?apikey=${apiKey}&ip=${resource}`;
        }
        else if (dataType == "domain") {
            url = `https://www.virustotal.com/vtapi/v2/url/report?apikey=${apiKey}&resource=${resource}`;
        }
        else if (dataType == "checksum") {
            url = `https://www.virustotal.com/vtapi/v2/file/report?apikey=${apiKey}&resource=${resource}`;
        }
        else {
            console.log("Something is very very wrong");
            return;
        }
          
        // Haetaan ajaxilla dataa VirusTotalin APIsta ja palautetaan tulos
        return $.ajax({ 
            url: url,
            type: "GET",
            dataType: "json",
            contentType: 'application/javascript',
            success:function(json){
                this.setState({totalvirus: json})
            }.bind(this)
        });
    }
	
	// Määrittelee miten VirusTotalin data renderöidään
    virusTotalBuild (data) {
        
        const items = [];
        
		// Jos annetun datan tyyppi on tarkistussumma tai domaini
		if(this.state.dataType == "checksum" || this.state.dataType == "domain") {
			// Jos annetun datan tyyppi on tarkistussumma, renderöidään siihen liittyvää APIlta saatua dataa
			if(this.state.dataType == "checksum") {
				items.push(
					<div className="virustotal-details">

						<h2>VirusTotal detection details</h2>
						<div className="virustotal-details-block"><div className="virustotal-details-header">Resource:</div><div className="virustotal-details-value">{data.resource}</div></div>

						<div className="virustotal-details-block"><div className="virustotal-details-header">SHA-1:</div><div className="virustotal-details-value">{data.sha1}</div></div>

						<div className="virustotal-details-block"><div className="virustotal-details-header">SHA-256:</div><div className="virustotal-details-value">{data.sha256}</div></div>

						<div className="virustotal-details-block"><div className="virustotal-details-header">MD5:</div><div className="virustotal-details-value">{data.md5}</div></div>

						<div className="virustotal-details-block"><div className="virustotal-details-header">Hits:</div><div className="virustotal-details-value">{data.positives}/{data.total}</div></div>

						<div className="virustotal-details-block"><div className="virustotal-details-header">VirusTotal link:</div><a className="virustotal-details-value" href={data.permalink}>{data.permalink}</a></div>

					</div>
				)
			}
			
			// Jos annetun datan tyyppi on domaini, renderöidään siihen liittyvää APIlta saatua dataa DOMiin
			if(this.state.dataType == "domain") {
				items.push(
					<div className="virustotal-details">

						<h2>VirusTotal detection details</h2>
						<div className="virustotal-details-block"><div className="virustotal-details-header">Resource:</div><div className="virustotal-details-value">{data.resource}</div></div>

						<div className="virustotal-details-block"><div className="virustotal-details-header">VirusTotal link:</div><div className="virustotal-details-value"><a href={data.permalink}>{data.permalink}</a></div></div>

						<div className="virustotal-details-block"><div className="virustotal-details-header">Scan date:</div><div className="virustotal-details-value">{data.scan_date}</div></div>

						<div className="virustotal-details-block"><div className="virustotal-details-header">Hits:</div><div className="virustotal-details-value">{data.positives}/{data.total}</div></div>

					</div>
				)
			}
            
            items.push(
				<div className="virustotal-databox">
					<div className="virustotal-resolutions-box-header">Antivirus vendor detections</div>
					<div className="virustotal-resolutions-box">{this.virustotalAVresults(data)}</div>
				</div>
			)
		}
		
		// Jos annetun datan tyyppi on IP-osoite
		if(this.state.dataType == "IPaddress") {
			
			items.push(
				<div className="virustotal-details">
				
					<h2>VirusTotal detection details</h2>
					<div className="virustotal-details-block"><div className="virustotal-details-header">Network:</div><div className="virustotal-details-value">{data.network}</div></div>
				
					<div className="virustotal-details-block"><div className="virustotal-details-header">AS owner:</div><div className="virustotal-details-value">{data.as_owner}</div></div>
				
					<div className="virustotal-details-block"><div className="virustotal-details-header">Country:</div><div className="virustotal-details-value">{data.country}</div></div>
				
					<div className="virustotal-details-block"><div className="virustotal-details-header">Continent:</div><div className="virustotal-details-value">{data.continent}</div></div>
				
					<div className="virustotal-details-block"><div className="virustotal-details-header">AS number:</div><div className="virustotal-details-value">{data.asn}</div></div>
					<div className="virustotal-databox">
						<div className="virustotal-resolutions-box-header">WHOIS information</div>
						<div className="virustotal-whois-box"><span className="virustotal-whois-text">{data.whois}</span></div>
					</div>

				</div>
			)
			
			items.push(
				<div className="virustotal-databox">
					<div className="virustotal-resolutions-box-header">Hostname resolutions</div>
					<div className="virustotal-resolutions-box">{this.addIPhostnameResolutions(data)}</div>
				</div>
			)
		}
        
        return items;
    }
	
	virustotalAVresults (data) {
        
        const items = [];
        
        // Renderöidään positiiviset AV osumat DOMiin
        for (let prop in data.scans) {
            if (data.scans[prop].detected == true) {
                items.push(
                    <div className="virustotal-result">
                        <div className="virustotal-avvendor">{prop}</div> <div className="virustotal-hit">{data.scans[prop].result}</div>
                    </div>
                ) 
            }
        }

        // Renderöidään negatiiviset AV osumat DOMiin - tuloste on vaihteleva datatyypistä riippuen
        for (let prop in data.scans) {
            if (data.scans[prop].detected == false) {
                if(this.state.dataType == "checksum") {
                    items.push(
                        <div className="virustotal-result">
                            <span className="virustotal-avvendor">{prop}</span><span className="virustotal-clean">Undetected</span>
                        </div>
                    )	
                }
                else if (this.state.dataType == "domain") {
                    items.push(
                        <div className="virustotal-result">
                            <span className="virustotal-avvendor">{prop}</span> <span className="virustotal-clean">{data.scans[prop].result}</span>
                        </div>
                    )
                } 
            }
        }
        
        return items;
    }
	
	// Luodaan lista IP osoitteisiin resolvaavista domaineista ja renderöidään se käyttäjälle
	addIPhostnameResolutions (data) {
		
		const items = [];
		
		for (let i = 0; i < Object.keys(data.resolutions).length; i++) {
			items.push(
				<div className="virustotal-result">
					<div className="virustotal-resolutions-hostname">{data.resolutions[i].hostname}</div>
					<div className="virustotal-resolutions-resolved">{data.resolutions[i].last_resolved}</div>	
				</div>
			)
		}	
		return items;
	}
	
	//Lähetetään URL urlscan:lle analysoitavaksi
	urlscanApiCall (resource) {
        
        let apiKey = "ae9e2c94-ab81-4371-89c2-95e1ecd1ace0";
		let url = "https://urlscan.io/api/v1/scan/";
		var result;
        
        // Haetaan ajaxilla dataa Urlscannin APIsta ja palautetaan tulos
        return $.ajax({ 
            url: url,
            type: "POST",
            cache: false,
			async: false,
            dataType: "json",
            data: {
                "url": resource,
                public: "off"
            },
			headers: {
				"API-Key": apiKey
			},
            // Jos tapahtuu virhe, annetaan urlscanState-muuttujalle arvo error jolloin
            // Käyttäjälle renderöidään ilmoitus virheestä
            error: function (request, textStatus, errorThrown) {
                console.log('Error');
                console.log(request.status);
                console.log(request.statusText);
                console.log(request.readyState);
                console.log(textStatus);
                console.log(errorThrown);
				this.setState({urlscanState: "error"})
            }.bind(this)
        })
    }
	
    // Tallennetaan urlscannin antama URL urlscanScanResultPage-objektiin.
    // Kyseisestä URLista haetaan hetken kuluttua valmis data toisella API-kutsulla
	setScanID (event) {
		
		this.setState({urlscanScanResultPage: event.api});
		/*
        if (tryAgain != true) {
           	this.setState({urlscanScanResultPage: event.api}); 
        }
        else {
            this.setState({urlscanScanResultPage: event});
        }
		*/
	}
	
	// Haetaan tiedot urlscanApiCall:issa lähetetystä pyynnöstä
	handleUrlScanData () {
        
		var url = this.state.urlscanScanResultPage;
		
        // Haetaan ajaxilla dataa urlscanin APIsta ja haun onnistuessa lisätään tulokset
        // state-objekteihin. Tällöin käyttäjälle renderöidään haun tulokset
		$.ajax({ 
			"url": url,
			type: "GET",
			cache: false,
			async: false,
			dataType: "json",
			success : function(json) {
				console.log("Success")
                console.log(json)
				this.setState({urlscan: json, urlscanState: "done"});
			}.bind(this)
		})
	}
	
	// Määrittelee miten urlscannin data renderöidään
	urlscanBuild (data) {
		
		const items = [];
		
		// Jos kaikki on mennyt hyvin, renderöidään urlscannilta saatu data DOMiin
		if(this.state.urlscanState == "done") {
			try {
				items.push(
					<div className="urlscan-details">

						<h2>Urlscan details</h2>

						<div className="urlscan-details-block"><img className="urlscan-details-block-thumbnail" src={data.task.screenshotURL}></img></div>

						<div className="urlscan-details-block"><div className="urlscan-details-header">URL:</div><div className="urlscan-details-value">{data.task.url}</div></div>

						<div className="virustotal-details-block"><div className="virustotal-details-header">IP address:</div><div className="virustotal-details-value">{data.meta.processors.geoip.data[0].ip}</div></div>

						<div className="virustotal-details-block"><div className="virustotal-details-header">Country:</div><div className="virustotal-details-value">{data.meta.processors.geoip.data[0].geoip.country_name}</div></div>

						<div className="virustotal-details-block"><div className="virustotal-details-header">City:</div><div className="virustotal-details-value">{data.meta.processors.geoip.data[0].geoip.city}</div></div>

						<div className="virustotal-details-block"><div className="virustotal-details-header">Urlscan report:</div><div className="virustotal-details-value"><a href={data.task.reportURL}>{data.task.reportURL}</a></div></div>

					</div>
				)
			}
			// Jos items-taulukkoon lisäämisen aikana tapahtuu jokin virhe
			catch(err) {
				console.log(err)
				items.push(
					<div className="urlscan-details">
						<h2>Urlscan details</h2>
						<div className="urlscan-details-block"><div className="urlscan-details-error">Unexpected error happened during processing of data!</div></div>
						<div className="urlscan-details-block"><div className="urlscan-details-error">Error has been logged to console.</div>
					</div></div>
				)
			}
		}
		// Kun tuloksia vielä odotellaan, renderöidään latausanimaatiota.
		else if(this.state.urlscanState == "waiting") {
			items.push(
				<div className="urlscan-details">
					<h2>Urlscan details</h2>
					<div className="urlscan-details-block"><img className="urlscan-details-loading-thumbnail" src="media/loading.gif"></img></div>
				</div>
			)
		}
        // Jos API kutsun aikana tapahtuu jokin virhe, renderöidään virheilmoitus
		else if(this.state.urlscanState == "error") {
			items.push(
				<div className="urlscan-details">
					<h2>Urlscan details</h2>
					<div className="urlscan-details-block"><div className="urlscan-details-error">Error happened during urlscan API call!</div></div>
					<div className="urlscan-details-block"><div className="urlscan-details-error">Error has been logged to console.</div></div>
				</div>
			)
		}
        // Muussa tapauksessa urlscanState-objektilla on outo arvo ja
        // on tapahtunut odottamaton virhe
		else {
			items.push(
				<div className="urlscan-details">
					<h2>Urlscan details</h2>
					<div className="urlscan-details-block"><div className="urlscan-details-error">Unknown error!</div></div>
				</div>
			)
		}
		return items;
		
	}
	
	// Kun käyttäjä painaa search nappia Intel-osiossa, kutsutaan tätä metodia.
    getResults (event) {
        
        event.preventDefault();
		
		// Tyhjennetään kaikki statet oletusarvoille
		this.setState({totalvirus: [], urlscan: {}, urlscanState: "", urlscanScanResultPage: {}, abuseipdb: {}, dataType: ""})
		
        // Tallennetaan haku-kentän arvo muuttujaan
        let searchData = this.refs.intelSearch.value;
        let dataType = "";
        
        // Tarkistetaan regexilla minkälaista dataa on syötetty; IP-osoite, verkkotunnus, tarkistussumma tai jotain muuta
        if(/^(?=.*[^\.]$)((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.?){4}$/igm.test(searchData)) {
            dataType = "IPaddress";
        }
        else if (/^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$/gm.test(searchData)) {
            dataType = "domain";
        }
        else if  (/^[a-f0-9]{32}$/gm.test(searchData.toLowerCase()) || /^[a-f0-9]{64}$/gm.test(searchData.toLowerCase()) || /^[a-f0-9]{96}$/gm.test(searchData.toLowerCase()) || /^[a-f0-9]{128}$/gm.test(searchData.toLowerCase())) {
            dataType = "checksum";
        }
        else {
            dataType = "unknown";
        }
		// Tallennetaan lisätty datatyyppi omaan stateen
		this.setState({dataType: dataType})
        
		if(dataType != "unknown") {
			// Jos TotalViruksen valintaruutu on valittuna, kutsutaan sen APIa
			if (this.refs.totalvirus.checked) {
				this.virustotalApiCall(searchData, dataType);
			}
            // Jos Urlscannin valintaruutu on valittuna, kutsutaan sen APIa
            // mikäli datatyyppi on verkkotunnus
			if (this.refs.urlscan.checked && (dataType != "checksum" && dataType != "IPaddress")) {
				this.setState({urlscanState: "waiting"});
				var urlscanResults = this.urlscanApiCall(searchData)
				.done(this.setScanID)
				.done(setTimeout(this.handleUrlScanData, 45000));
			}
			
            // Jos AbuseIPDBn valintaruutu on valittuna, kutsutaan sen APIa
            // Mikäli datatyyppi on IP-osoite
			if (this.refs.abuseipdb.checked && dataType == "IPaddress") {
				this.abuseipdbApiCall(searchData);
			}
		}

    }
	
    // Lähetetään IP-osoite AbuseIPDB:lle
	abuseipdbApiCall (data) {
		
		var apiKey = "7e10002d3ccb67f528f2abda096154e2872d6132244b6e3262a5380aa87f1a9b16f744e2540a7789";
		var days = "14";	
		var url = `https://www.abuseipdb.com/check/${data}/json?key=${apiKey}&days=${days}&verbose`;
        
        // Haetaan ajaxilla dataa AbuseIPDB:n APIsta ja tallennetaan tulos abuseipdb-objektiin
		$.ajax({ 
			"url": url,
			type: "GET",
			cache: false,
			async: false,
			dataType: "json",
			success : function(json) {
				console.log("Success")
				console.log(json);
				this.setState({abuseipdb: json});
			}.bind(this)
		})		
	}
	
    // Määrittelee miten AbuseIPDB:n data renderöidään
	abuseipdbBuild (data) {
		
		const items = [];
		
        // Jos prosessi on sujunut tähän asti onnistuneesti, renderöidään AbuseIPDB:n APIlta saatu data DOMiin
		try {
			items.push(
				<div className="abuseipdb-details">

					<h2>AbuseIPDB detection details</h2>
					<div className="abuseipdb-details-block"><div className="abuseipdb-details-header">IP:</div><div className="abuseipdb-details-value">{data[0].ip}</div></div>

					<div className="abuseipdb-details-block"><div className="abuseipdb-details-header">Country:</div><div className="abuseipdb-details-value">{data[0].country}</div></div>

					<div className="abuseipdb-details-block"><div className="abuseipdb-details-header">Abuse confidence score:</div><div className="abuseipdb-details-value">{data[0].abuseConfidenceScore}</div></div>

				</div>
			)
			
			items.push(
				<div className="abuseip-report-box">
					<div className="abuseipdb-report-box-header">Reports</div>
					<div className="abuseipdb-resolutions-box">{this.abuseipdbReports(data)}</div>
				</div>
			)		
		}
        // Jos items-taulukkoon lisäämisen aikana tapahtuu jokin virhe
        // Tulostetaan renderöidään näkyville virheilmoitus
		catch(error) {
			console.log(error)
			items.push(
				<div className="abuseipdb-details">
					<h2>AbuseIPDB detection details</h2>
					<div className="urlscan-details-block"><div className="urlscan-details-error">Unexpected error happened during processing of data!</div></div>
					<div className="urlscan-details-block"><div className="urlscan-details-error">Error has been logged to console.</div></div>
				</div>
			)
		}
	
		return items;
	}

    // renderöidään boxi, johon lisätään kaikki API:lta saadut hälytykset 
    // sille syötetystä IP-osoitteesta sekä kommentit jokaisesta hälytyksestä
	abuseipdbReports (data) {
		
		const items = []
		
		for (let i = 0; i < Object.keys(data).length; i++) {
			console.log(data[i])
			items.push(
				<div className="virustotal-result">
					<div className="abuseipdb-report-created">{data[i].created}</div>
					<div className="abuseipdb-report-comment">{data[i].comment}</div>	
				</div>
			)
		}
		return items;
	}
	
    // Intel-komponentin renderöinti
    render() {
        
        // Lisätään kaikki elementit items-taulukkoon
        const items = [];
        
        items.push(
            <div className="intel-box">
                <h1 className="search-box-header">Threat intelligence search</h1>
                <form className="intel-search-form" onSubmit={this.getResults}>
                    <input className="intel-search-box" placeholder="Type in domain, IP address or hash" ref="intelSearch" ></input><br></br>
                    <input className="intel-search-checkbox" type="checkbox" ref="totalvirus" ></input>Virustotal
                    <input className="intel-search-checkbox" type="checkbox" ref="urlscan" ></input>Urlscan
                    <input className="intel-search-checkbox" type="checkbox" ref="abuseipdb" ></input>AbuseIPDB 
                    <button type="submit" className="search-box-button">Search</button>      
                </form>
            </div>
        )
		
        // Jos käyttäjän antamaa datatyyppiä ei tunnisteta, renderöidään virheilmoitus
		if (this.state.dataType == "unknown") {
			items.push(
				<div className="intel-error-message">
					<h3>Invalid data given!</h3>
					<p>Search accepts IP address, hash or domain.</p>
				</div>
			)
		}
		
		// Jos totalvirus-objekti ei ole tyhjä, yritetään renderöidä objektista löytyvä data
        if (!(jQuery.isEmptyObject(this.state.totalvirus))) {
            items.push(
                <div className="virustotal-box">
                    {this.virusTotalBuild(this.state.totalvirus)}
                </div>
            )
        }
		
        // Jos apuseipdb-objekti ei ole tyhjä, yritetään renderöidä objektista löytyvä data
		if (!(jQuery.isEmptyObject(this.state.abuseipdb))) {
            items.push(
                <div className="abuseipdb-box">
                    {this.abuseipdbBuild(this.state.abuseipdb)}
                </div>
            )
        }
		
        // Jos urlscanState-objekti ei ole tyhjä, yritetään renderöidä urlscan-objektista löytyvä data 
		if (this.state.urlscanState.length != 0) {
            items.push(
                <div className="urlscan-box">
                    {this.urlscanBuild(this.state.urlscan)}
                </div>
            )
        }
		
        // Palautetaan tulokset ylempään komponenttiin PageSelect, joka tulostaa renderöi ne
        return (
            <div className="intel-page">
                {items}
            </div>
        )
    }
}

class News extends React.Component {
    constructor(props) {
        super(props);
        this.state = {RSSfeeds: {}, RSSfeedsFiltered: {}, selectValue: "latest"}
        this.loadRSS = this.loadRSS.bind(this);
        this.filterResults = this.filterResults.bind(this);
        this.tagFilter = this.tagFilter.bind(this);
        this.thumbnailExists = this.thumbnailExists.bind(this);
        this.selectFilterUpdate = this.selectFilterUpdate.bind(this);
    }
	
	//Kun News-komponentti on ensimmäisen kerran renderöity puuhun -->
    componentDidMount() {
        
        this._isMounted = true;  
        var RSSresults;
        var RSSfeedsFilter = "latest";
        
		// Jos ajax-pyynnön tuloksia ei ole tallennettu ylempään komponenttiin, kutsutaan loadRSS-metodia
        if (Object.entries(this.props.RSSfeeds).length === 0 && this.props.RSSfeeds.constructor === Object) {
            RSSresults = this.loadRSS();
        }
		// Jos sivu on ladattu aiemmin ja sen tulokset on tallennettu ylempään komponenttiin
        else {
            RSSresults = this.props.RSSfeeds;
            RSSfeedsFilter = this.props.selectFilter;
            this.refs.filter.value = this.props.feedFilter;
        }
        // Uudelleen renderöidään komponentti ja filtteröidään tulokset
        this.setState({RSSfeeds: RSSresults, RSSfeedsFiltered: RSSresults, selectValue: RSSfeedsFilter}, () => {
            this.filterResults();
        });
    }
    
    // Tallennetaan ajax-pyynnön tulokset ylempään komponenttiin, tämän komponentin tuhoutuessa
    componentWillUnmount () {
        console.log(this.state.selectValue)
        this.props.saveRSSfeedsResults(this.state.RSSfeeds, this.state.selectValue, this.refs.filter.value);
    }
    
    // Hakee uutiset halutuista lähteistä (RSSfeeds), lisää ajax pyyntöjen tulokset yksikerrallaan RSSresults-objektin sisälle ja lopuksi palauttaa kyseisen objektin
    loadRSS () {
        
        const RSSfeeds = {
			threatpost: "https://threatpost.com/feed/",
            wired: "https://www.wired.com/category/security/feed/",
			bleepingcomputer: "https://www.bleepingcomputer.com/feed/",
			techrepublic: "https://www.techrepublic.com/rssfeeds/topic/security/",
			jeffsoh: "https://nakedsecurity.sophos.com/feed/"
			//kaspersky: "https://www.kaspersky.co.uk/blog/feed/"
			//cyware: "https://cyware.com/allnews/feed"
        };
        
        var RSSresults = {};
        var iterator = 0;
        
        // Haetaan jokaisesta RSSfeedistä dataa yksi kerrallaan antamalla feedin URL parametriksi
        // news.php skriptille, joka hakee datan URL:ista ja palauttaa tulokset
        // Takaisin tuleva data on XML:ää
		$.when(Object.keys(RSSfeeds).forEach(function(feed) {
            $.ajax({       
            url: "php/news.php",
            async: false,
            dataType:'xml',
			data: {url: RSSfeeds[feed]},
            success:function(xml){
                $(xml).find("channel").each(function(){
                    // Luodaan jokaiselle yksittäiselle uutiselle oma objekti RSSresults-objektin sisälle
                    $(this).find("item").each(function(){
                        
                        // Lisätään uutisesta löytyvät kategoriat taulukkoon
                        // Ne renderöidään myöhemmin tageina uutiseen
                        let categories1 = [];
                        $(this).find("category").each(function(){
                            categories1.push($(this).text()) 
                        });
                        
                        let title1 = $(this).find("title").text();
                        let link1 = $(this).find("link").text();
                        let description1 = $(this).find("description").text();
                        let pubDate1 = $(this).find("pubDate").text();
                        let postDate = new Date(pubDate1);
                        let thumbnail1 = $(this).find("media\\:thumbnail").attr("url");
                        
                        RSSresults[iterator] = {link:link1, title:title1, description:description1, pubDate:postDate, thumbnail:thumbnail1, categories: categories1, source: feed};
                        iterator += 1;
                    });
                });  
            }
        })}))
        .done(function() {
            console.log("Done");
        })
        .fail(function() {
            console.log("Fail");
        });
        
        // Palautetaan lopuksi objekti, josta löytyy jokaisen RSSfeedin data erikseen
        return RSSresults;
    }
    
    // Kun käyttäjä lajittelee uutiset aakkosjärjestyksessä tekijän mukaan
    // tai julkaisupäivämäärän (oletus) mukaan, kutsutaan tätä metodia
    // ja päivitetään selectValue-objektille hakukentässä oleva arvo,
    // sekä kutsutaan filterResults metodia.
    selectFilterUpdate (event) {
        this.setState({selectValue: event.target.value}, () => {
            this.filterResults();
        });
    }
    
    // Lisätään tagin merkkijono input-filtteriin ja päivitetään tulokset
    tagFilter (tag) {
        $(this.refs.filter).val(tag);
        this.filterResults();
    }
    
    // Jos käyttäjä filtteröi uutisia uutuusjärjestyksessä, tai tekijän mukaan
    // Kutsutaan tätä metodia ja palautetaan uutiset valitussa järjestyksessä
    filterBySelect (RSSresults) {
        
        var valuesSorted = {};
        var newIndex = 0;
        
        // Palautetaan uutiset uusimmasta vanhimpaan
        if(this.state.selectValue == "latest") {
            
            Object.keys(RSSresults).sort(function(a, b)
                    {return RSSresults[b].pubDate.getTime() - RSSresults[a].pubDate.getTime()})
            .forEach(function(key) {
                valuesSorted[newIndex] = RSSresults[key];
                newIndex += 1;
            })
            return valuesSorted;
        }
        
        // Palautetaan uutiset vanhimmasta uusimpaan
        else if(this.state.selectValue == "oldest") {
            
            Object.keys(RSSresults).sort(function(a, b)
                    {return RSSresults[a].pubDate.getTime() - RSSresults[b].pubDate.getTime()})
            .forEach(function(key) {
                valuesSorted[newIndex] = RSSresults[key];
                newIndex += 1;
            })         
            return valuesSorted;      
        }
        
        // Palautetaan uutiset lähteen mukaan aakkosjärjestyksessä
        else if(this.state.selectValue == "alphabetical") {
            
            Object.keys(RSSresults).sort(function(a, b)
                    {return RSSresults[a].source.localeCompare(RSSresults[b].source);})
            .forEach(function(key) {
                valuesSorted[newIndex] = RSSresults[key];
                newIndex += 1;
            })        
            return valuesSorted;           
        }
        
        // Palautetaan uutiset lähteen mukaan käänteisessä aakkosjärjestyksessä
        else if(this.state.selectValue == "reverseAlphabetical") {
            
            Object.keys(RSSresults).sort(function(a, b)
                    {return RSSresults[b].source.localeCompare(RSSresults[a].source);})
            .forEach(function(key) {
                valuesSorted[newIndex] = RSSresults[key];
                newIndex += 1;
            })          
            return RSSresults;
        }
        
        else {
            return RSSresults;
        }
    }
    
    // Käyttäjän kirjoittaessa uutisten suodatuskenttään kutsutaan tätä metodia
    // Palautetaan ne uutiset jotka sisältävät käyttäjän kirjoittaman merkkijonon
    filterResults () {
        
        var filter = this.refs.filter.value;
        var RSSresults = this.state.RSSfeeds;
        var FilteredResults = {};
        console.log(filter)

        RSSresults = this.filterBySelect(RSSresults);
        
        // Jos merkkijono-filtteriä ei ole, näytetään kaikki ajaxin palauttamat uutiset
        if (filter == "") {
            this.setState({RSSfeedsFiltered: RSSresults});
            return;
        }
        
        var index = 0;
        
        for (let i = 0; i < Object.keys(RSSresults).length; i++) {
            
            // Palautetaan uutinen jos sen tittelistä, kuvauksesta, linkistä tai kategoriasta löytyy filtterinä käytetty merkkijono
            if(RSSresults[i].title.toLowerCase().includes(filter.toLowerCase()) || RSSresults[i].description.toLowerCase().includes(filter.toLowerCase()) ||
            RSSresults[i].link.toLowerCase().includes(filter.toLowerCase()) ||
			RSSresults[i].categories.find(function(tag) {
				return tag.toLowerCase().includes(filter.toLowerCase())
			}))
            {
                FilteredResults[index] = RSSresults[i];
                index += 1;
            }  
            else {
                continue;
            }
        }
        this.setState({RSSfeedsFiltered: FilteredResults});
    }
    
    // Jos uutinen sisältää thumbnailin, palautetaan sen linkki
    thumbnailExists (thumbnail, link) {
        if (typeof thumbnail != "undefined") {
            return <a  href={link}><img className="news-thumbnail" src={thumbnail}></img></a>
        }
    }
    // News-komponentin renderöinti
    render() {
        
        var RSSfeeds = this.state.RSSfeedsFiltered;     
        const items = []
        
        items.push(
            <div className="search-box">
                <h1 className="search-box-header">Filter news</h1>
                <div>
                    <input placeholder="Phrase filter" ref="filter" onChange={this.filterResults} ></input>
                    <select value={this.state.selectValue} onChange={this.selectFilterUpdate} >
                      <option value="latest">Latest news first</option>
                      <option value="oldest">Oldest news first</option>
                      <option value="alphabetical">A-Z by author</option>
                      <option value="reverseAlphabetical">Z-A by author</option>
                    </select>
                </div>
                <button className="search-box-button" onClick={this.loadRSS}>Refresh page</button>
            </div>
        )
        
        // Renderöidään uutiset yksikerrallaan
        for (var i = 0; i < Object.keys(RSSfeeds).length; i++) {
            items.push(
                <div className="news-box">
                    {this.thumbnailExists(RSSfeeds[i].thumbnail, RSSfeeds[i].link)}
                    <a className="news-title"  href={RSSfeeds[i].link}>{RSSfeeds[i].title}</a>
                    <p className="news-text">{RSSfeeds[i].description}</p>
                    <p >{RSSfeeds[i].pubDate.toString().split(' ').slice(0, 6).join(' ')}</p>
                    {RSSfeeds[i].categories.map(tag => (
                        <p onClick={() => this.tagFilter(tag)} className="search-tag">{tag}</p>
                    ))}
                </div> 
            );
        }
        
        return (
            <div>
                {items}
            </div>
        )
    }
}

// News ja Intel komponenttien yläkomponentti
class PageSelect extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
                RSSfeeds: {}, feedFilter: "", selectFilter: "",
                virustotal: {}, abuseipdb: {}, urlscan: {}, urlscanState: {}, urlscanScanResultPage: {}, intelSearch: "", dataType: ""
        }
        this.saveRSSfeedsResults = this.saveRSSfeedsResults.bind(this);
        this.saveIntelResults = this.saveIntelResults.bind(this);
    }
    
    // Tallennetaan ajaxista haettujen News-komponentin RSSfeedien tulokset ja suodatukset
    // Jotta ne voidaan tulostaa uudestaan News komponenttia renderöitäessä
    // Eikä uutisia tarvitse hakea uudelleen ajaxilla
    saveRSSfeedsResults (RSSfeedResults, RSSfeedSelectFilter, FeedSearchValue) {
        this.setState({RSSfeeds: RSSfeedResults, selectFilter: RSSfeedSelectFilter, feedFilter: FeedSearchValue})
    }
    
	// Tallennetaan ajaxista haettujen Intel-komponentin APIen tulokset
    // jotta ne voidaan tulostaa uudestaan Intel komponenttia renderöitäessä
    // Eikä API kutsuja tarvitse tehdä uudelleen ajaxilla
    saveIntelResults (virustotalResults, abuseipdbResults, urlscanResults, searchValue, dataType, urlscanState, urlscanScanResultPage) {
        console.log(virustotalResults)
        this.setState({virustotal: virustotalResults, abuseipdb: abuseipdbResults, urlscan: urlscanResults, intelSearch: searchValue, dataType: dataType, urlscanState: urlscanState, urlscanScanResultPage: urlscanScanResultPage})
    }
    
    // Määrittelee renderöidäänkö News vai Intel komponentti
    checkPage () {
        if (this.props.pageName == "News") {
            console.log("News")         
            return(
                <News RSSfeeds={this.state.RSSfeeds}
                saveRSSfeedsResults={this.saveRSSfeedsResults}
                selectFilter={this.state.selectFilter}
                feedFilter={this.state.feedFilter} 
                />
            )       
        }
        else if (this.props.pageName == "Intel") {
           console.log("Intel")
            return(
                <Intel saveIntelResults={this.saveIntelResults}
                virustotal = {this.state.virustotal}
                abuseipdb = {this.state.abuseipdb}
                urlscan = {this.state.urlscan}
                urlscanState = {this.state.urlscanState}
                urlscanScanResultPage = {this.state.urlscanScanResultPage}
                intelSearch = {this.state.intelSearch}
                dataType = {this.state.dataType}              
                />
            )
        }
    }
      
    render() {
        return (
            <div>
                {this.checkPage()}
            </div>
        )
    }
}

// Pääkomponentti, jonka alla kaikki muut komponentit ovat
class Content extends React.Component {
    
    constructor(props) {
        super(props);
        this.state = {pageName: "News"};
        this.pageChange = this.pageChange.bind(this);
    }
    // Annetaan pageName objektille joko "News" tai "Intel" arvoksi
    // Määrittelee kumpi sivu käyttäjälle näytetään
    pageChange (event) {
        this.setState({pageName: event.target.text})
    }
    
    render() {
        return (
            <div id="main">
                <h1 className="header">ThreatLab</h1>
                <div className="pages">
                    <a className="page-name" href="#" onClick={(evt) => this.pageChange(evt)}>News</a> 
                    <span className="page-bar">|</span> 
                    <a className="page-name" href="#" onClick={(evt) => this.pageChange(evt)}>Intel</a>
                </div>
                <PageSelect pageName={this.state.pageName} />
            </div>
        )
    }
}

ReactDOM.render(
    <Content />,
    document.getElementById('content')
);