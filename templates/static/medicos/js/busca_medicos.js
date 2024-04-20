// templates/static/medicos/js/busca_medicos.js

(function($) {
    window.getInfo = getInfo;
    window.captchaV2value = false;
    window.currentPage = '';
    
    var initGet = false;
    var resultado = [];
    var page = 1;
    var pageSize = 10;



    var $select_municipio, select_municipio;


    window.onlyNumberKey = function(evt) {
            
            // Only ASCII character in that range allowed
            var ASCIICode = (evt.which) ? evt.which : evt.keyCode
            //console.log(evt.key);
            if (ASCIICode == 8 || ASCIICode == 46 || ASCIICode == 37 || ASCIICode == 38 || ASCIICode == 39 || ASCIICode == 40 || !isNaN(evt.key) )
                return true;
            return false;
        }

    $('#buscaForm').on('submit', function(e) {
    e.preventDefault();

    if(recaptchaPublicKeyV2){
        grecaptcha.reset();
        grecaptcha.execute();
    } else {
        getInfo();
    }
    });

    //  $(document).on('click', '.btnPesquisar', function(e) {

    //  });

    function getInfo(pageA = 1, rerender = true) {
    if(recaptchaPublicKeyV2){
    onGetInfo(pageA, rerender);
    } else {
    window.reloadCaptcha(function() {
        onGetInfo(pageA, rerender);
    });
    }

    }

    function onGetInfo(pageA = 1, rerender = true) {
    var moreInfo = $(this).data('more');
    var formData = {};
    $('#buscaForm').serializeArray().forEach(function(item) {
        formData[item.name] = item.value;
    })
    //  console.log(formData);

    // if (moreInfo) {
    //   $(this).parent('.paginacao').remove();
    // } else {
    //   $(".busca-resultado").html('');
    //   page = 1;
    // }

    if(recaptchaPublicKeyV2){
    window.captchaV2value = true;
    console.log('UsingV2');
    } else {
    window.captchaV2value = false;
    console.log('UsingV3');
    }

    //Bug Fix 
    if(isNaN(pageA)){
        pageA = 1;
    }

    var payload = [{
        useCaptchav2: window.captchaV2value,
        captcha: formData["g-recaptcha-response"],
        medico: {
        nome: formData.nome,
        ufMedico: formData.uf,
        crmMedico: formData.crm,
        municipioMedico: formData.municipio,
        tipoInscricaoMedico: formData.inscricao,
        situacaoMedico: formData.tipoSituacao,
        detalheSituacaoMedico: formData.situacao,
        especialidadeMedico: formData.especialidade,
        areaAtuacaoMedico: formData.areaAtuacao
        },
        page: pageA,
        pageNumber: pageA,
        pageSize: pageSize
    }];

    //BRUNO newRota(payload);
    $("#resultados").html('');

    //  $('html, body').animate({
    //    scrollTop: $('.btn-buscar').offset().top
    //  }, 500);


    $.ajax(window._API.endpoint + '/medicos/buscar_medicos', {
        method: 'post',
        dataType: 'json',
        data: JSON.stringify(payload),
        beforeSend: function() {
            $('.loading').css("display", "flex");
        },
        }).done(function(result) {

        if(recaptchaPublicKeyV2){
            if(result && (result == 'expirou' || result == 'invalidinput')){
            console.log('invalidInput');
            $(".busca-resultado").css("display", "none");
            //alert('Tempo limite de busca atingido. Refaça a captcha.');
            $('.loading').css("display", "none");
            grecaptcha.reset();
            grecaptcha.execute();
            return;
            }
        }
        $(".busca-resultado").css("display", "block");
        $(".btn-buscar").html("Buscar");
        $(".busca-resultado").html('');
        if (result && result.status && result.dados) {
        


            if (result.dados.length) {
            result.dados.forEach(function(item, index) {
                var listEspecialidades = item.ESPECIALIDADE ? item.ESPECIALIDADE.split('&') : [];
                var nameEspec = '';
                listEspecialidades.map(e => {
                if (e !== '') {
                    nameEspec += e + '<br />';
                }
                });
                if(item.PRIM_INSCRICAO_UF == null) {
                    item.PRIM_INSCRICAO_UF = 'Informação não disponível';
                }
                var html = '<div class="resultado-item resultMedico_' + index + ' medico_' + item.SG_UF + '_' + item.NU_CRM + '">';
                html += '    <div class="card picture-left">';
                html += '      <div class="row align-items-center">';
                html += '        <div class="col-12 col-md-auto text-center">';
                html += '          <div class="picture">';
                html += '            <img src="https://portal.cfm.org.br/wp-content/themes/portalcfm/assets/images/no-picture.svg" alt="">';
                html += '          </div>';
                html += '        </div>';
                html += '        <div class="col">';
                html += '          <div class="card-body">';
                if(!!item.NM_SOCIAL){
                html += '            <h4 style="margin:0;">' + item.NM_SOCIAL + ' (nome social/indígena)</h4>';
                html += '            <h2 class="mb-4">' + item.NM_MEDICO + ' (nome de registro)</h2>';
                } else {
                html += '            <h4>' + item.NM_MEDICO + '</h4>';
                }
                html += '            <div class="row">';
                html += '              <div class="col-md-4">';
                html += '                <b>CRM:</b> ' + item.NU_CRM + "-" + item.SG_UF;
                html += '              </div>';
                html += '              <div class="col-md-4">';
                html += '                <b>Data de Inscrição:</b> ' + (item.DT_INSCRICAO ? item.DT_INSCRICAO : '');
                html += '              </div>';
                html += '              <div class="col-md-4">';
                html += '                <b>Primeira inscrição na UF:</b> ' + item.PRIM_INSCRICAO_UF;
                html += '              </div>';
                html += '            </div>';
                html += '            <div class="row">';
                html += '              <div class="col-md-6">';
                html += '                <b>Inscrição:</b> ' + item.TIPO_INSCRICAO;
                html += '              </div>';
                html += '              <div class="col-md">';
                html += '                <b>Situação:</b> ' + item.SITUACAO + '<span id="doc'+item.NU_CRM+item.SG_UF+'"></span>';
                html += '              </div>';
                html += '            </div>';
                html += '            <div class="row item_outro_estado" style="display: none;">';
                html += '              <div class="col-md-12">';
                html += '                <b>Inscrições em outro estado:</b> <span></span>';
                html += '              </div>';
                html += '            </div>';

                nameEspec2 = '';
                if (!nameEspec) {
                nameEspec2 = '<span style="color:#191a1a;">&nbsp;Médico sem especialidade registrada.</span>';
                }

                html += '            <div class="row">';
                html += '              <div class="col-md-12" style="display: flex;">';
                html += '                 <b>Especialidades/Áreas de Atuação:</b>'+nameEspec2;
                html += '              </div>';
                html += '            </div>';
                if (nameEspec) {
                html += '            <div class="row"><div class="col-md-12">' + nameEspec + '</div></div>';
            }

            // }

                html += '            <div class="row endereco"  style="display: none;">';
                html += '              <div class="col-md-12">';
                html += '                <b>Endereço:</b> ';
                html += '              </div>';
                html += '            </div>';
                html += '            <div class="row telefone"  style="display: none;">';
                html += '              <div class="col-md-12">';
                html += '                <b>Telefone(s):</b> ';
                html += '              </div>';
                html += '            </div>';
                html += '              <div class="row visto_provisorio" style="display: none;"><div class="col-md-12">';
                html += '                <b>Visto(s) Temporário(s) ativo(s): <span></span></b>';
                html += '              </div></div>';
                html += '          </div>';
                html += '        </div>';
                html += '      </div>';
                html += '    </div>';
                html += '  </div>';
                $(".busca-resultado").append(html);
                getMoreInfo(item.NU_CRM_PLAIN, item.SG_UF, item.SECURITYHASH, index);
                // resultado.push(item.COUNT);    
                $.ajax('https://portal.cfm.org.br/wp-content/themes/portalcfm/assets/php/documento_medico.php?crm='+item.NU_CRM_PLAIN+'&uf='+item.SG_UF+'&hash='+item.SECURITYHASH+'&check=true',{
                async: 'false',
                method: 'get',
                }).done(function(res) {
                    if(res == 1){
                    docLink = ' <a href="https://portal.cfm.org.br/wp-content/themes/portalcfm/assets/php/documento_medico.php?crm='+item.NU_CRM_PLAIN+'&uf='+item.SG_UF+'&hash='+item.SECURITYHASH+'" target="_blank" style="font-variant: small-caps;">(documento de decisão)</a>';
                    jQuery('#doc'+item.NU_CRM+item.SG_UF).append(docLink);     
                    }  

                });

            });
            resultado = result.dados[0].COUNT;
            if (resultado > 0) {

            var htmlResultados = `<div class="text-center">${resultado} registros encontrados</div>`;

            $("#resultados").html(htmlResultados);

                // var qtdPaginas = parseInt(resultado[0]) / parseInt(pageSize);
                // var qtdPaginasTrat = qtdPaginas.toLocaleString('pt-BR', {
                //   currency: 'BRL'
                // });
                // var qtdRegistros = parseInt(resultado[0]).toLocaleString('pt-BR', {
                //   currency: 'BRL'
                // });
                // let htmlPagination = `
                //   <div class="paginacao">
                //     <button class="btn-more btnPesquisar" data-more='yes'>Ver mais</button>
                //     <p>Mostrando página ${page} de ${parseFloat(qtdPaginasTrat)}</p>
                //     <p>${qtdRegistros} registros encontrados</p>
                //   </div>
                //   `;
                // $(".busca-resultado").append(htmlPagination);
                // page++;
                if (rerender) {
                renderPagination(pageA);
                }
                initGet = true;
                $('.loading').css("display", "none");
            }
            } else {
            var html = '<div class="resultado-item">';
            html += '<p>Nenhum resultado encontrado</p>';
            html += '</div>';
            $(".busca-resultado").html(html);
            $('.loading').css("display", "none");
            }
            $('.loading').css("display", "none");
            //  $('html, body').animate({
            //    scrollTop: $('.btn-buscar').offset().top - 200
            //  }, 500);
        }
        })
        .fail(function(jqXHR, textStatus, msg) {

            alert('Houve um erro ao efetuar sua busca, por favor, tente mais tarde!');
        $(".btn-buscar").html("Buscar");
        

        });
    return false;
    };

    function getMoreInfo(crm, uf, securityHash, index) {
    //  window.reloadCaptcha(function() {
    //    onGetMoreInfo(crm, uf, index);
    //  });
    onGetMoreInfo(crm, uf, securityHash,  index);
    }

    function onGetMoreInfo(crm, uf, securityHash, index) {

    const captcha = $('input[name="g-recaptcha-response"]').val();

    $.ajax(window._API.endpoint + '/medicos/buscar_foto/',{
    method: 'post',
        dataType: 'json',
        data: JSON.stringify([{securityHash: securityHash, crm: crm, uf: uf}]),

    }).done(function(res) {;
        if (res && res.status && res.dados) {
        var values = res.dados[0];
        if (values.AUTORIZACAO_IMAGEM !== "N"/* && values.IMAGEM*/) {
            $('.resultMedico_' + index + ' .picture').html('<img src="https://portal.cfm.org.br/wp-content/themes/portalcfm/assets/php/foto_medico.php?crm='+values.CRM+'&uf='+values.UF_CRM+'&hash='+values.HASH+'" onerror="this.onerror=null;this.src=\'https://portal.cfm.org.br/wp-content/themes/portalcfm/assets/images/no-picture.svg\';" >');
            //$('.resultMedico_' + index + ' .picture').html('<img src="data:image/png;base64, ' + values.IMAGEM +
            //  '" >');
        }

        if (values.AUTORIZACAO_ENDERECO == "S") {
            $('.resultMedico_' + index + ' .card-body .endereco').html("<div class='col-md-7'><b>Endereço:</b> " +
            values.ENDERECO + '</div>');
            $('.resultMedico_' + index + ' .card-body .endereco').show();
        } else {
            $('.resultMedico_' + index + ' .endereco').html(
            "<div class='col-md-7'><b>Endereço:</b> Exibição não autorizada pelo médico." + '</div>');
            $('.resultMedico_' + index + ' .endereco').show();
        }
        if (values.TELEFONE && values.AUTORIZACAO_ENDERECO == "S") {
            $('.resultMedico_' + index + ' .telefone').html("<div class='col-md-7'><b>Telefone:</b> " + values
            .TELEFONE + '</div>');
            $('.resultMedico_' + index + ' .telefone').show();
        } else {
            $('.resultMedico_' + index + ' .telefone').html(
            "<div class='col-md-7'><b>Telefone:</b> Exibição não autorizada pelo médico." + '</div>');
            $('.resultMedico_' + index + ' .telefone').show();
        }

        if (values.INSCRICAO) {
            $('.resultMedico_' + index).find(".item_outro_estado").show();
            $('.resultMedico_' + index).find(".item_outro_estado span").html(values.INSCRICAO);
        }

        if (values.VP_DESTINO) {
            $('.resultMedico_' + index).find(".visto_provisorio").show();
            if(res.dados.length > 1){
            elstring = '';
            res.dados.forEach(function(el){
                elstring += 'CRM-'+el.VP_DESTINO+' de '+el.VP_INICIO+' à '+el.VP_FIM+'<br>';
            })
            
            $('.resultMedico_' + index).find(".visto_provisorio span").html('<div>'+elstring+'</div>');  
            } else {
            $('.resultMedico_' + index).find(".visto_provisorio span").html('CRM-'+values.VP_DESTINO+' de '+values.VP_INICIO+' à '+values.VP_FIM);   
            }

        }           
        }
    });
    }

    function buscarEspecialidadeMedico(id) {
        const captcha = $('input[name="g-recaptcha-response"]').val();
    $.ajax(window._API.endpoint + '/medicos/buscar_foto/', {
    method: 'post',
        dataType: 'json',
    data: JSON.stringify([{captcha: captcha, crm: crm, uf: uf}]),
    }).done(function(res) {
        if (res && res.status && res.dados) {
        var values = res.dados[0];
        if (values.AUTORIZACAO_IMAGEM && values.IMAGEM) {
            $('.resultMedico_' + index + ' .picture').html('<img src="' + values.IMAGEM + '" >');
        }
        if (values.AUTORIZACAO_ENDERECO && values.ENDERECO) {
            $('.resultMedico_' + index + ' .endereco').html("<b>Endereço:</b> " + values.ENDERECO);
        }
        }
    });
    }

    function listarUFs() {
    $.ajax(window._API.endpoint + '/medicos/listar_ufs', {
        dataType: 'json'
    }).done(function(res) {
        if (res && res.status && res.dados) {
        var ufs = [];
        res.dados.forEach(function(item) {
            $("#uf").append('<option value="' + item.SG_UF + '">' + item.SG_UF + '</option>');
        });

        //  setTimeout(function() {
        //    restoreRota();
        //    $("#uf").trigger("change");
        //  }, 100);
        }
    });
    }

    $("#uf").change(function(e) {
    var uf = e.target.value;
    if (uf === 'RJ') {
        $('.basic-addon').show();
        $('.controll-state').addClass('selectRJ');
    } else {
        $('.basic-addon').hide();
        $('.controll-state').removeClass('selectRJ');
    }
    $.ajax(window._API.endpoint + '/medicos/listar_municipios/' + uf, {
        dataType: 'json'
    }).done(function(res) {
        if (res && res.status && res.dados) {
        var municipios = [];
        $("#municipio").html('');
        $("#municipio").append('<option value="">Todos</option>');
        res.dados.forEach(function(item) {
            $("#municipio").append('<option value="' + item.ID_MUNICIPIO + '">' + item.DS_MUNICIPIO +
            '</option>');
            //  municipios.push({
            //    text: item.DS_MUNICIPIO,
            //    value: item.ID_MUNICIPIO
            //  });
        })

        //  select_municipio.options = municipios;
        //  select_municipio.refreshOptions();

        }
    });
    });

    function listarEspecialidades() {
    $.ajax(window._API.endpoint + '/medicos/listar_especialidades', {
        dataType: 'json'
    }).done(function(res) {
        if (res && res.status && res.dados) {
        var especialidades = [];
        res.dados.forEach(function(item) {
            $("#especialidade").append('<option value="' + item.ID_ESPECIALIDADE + '">' + item
            .DS_ESPECIALIDADE + '</option>');
        })
        }
    });
    }

    $(".limpaArea").click(function() {
    $("#especialidade").val('');
    valuesEspecilidades('', true);
    });

    $("#especialidade").change(function(e) {
    valuesEspecilidades(e);
    });

    function valuesEspecilidades(e, limp) {
    var especialidade = limp ? '' : e.target.value;
    $.ajax(window._API.endpoint + '/medicos/buscar_areas_atuacao/' + especialidade, {
        dataType: 'json'
    }).done(function(res) {
        $("#areaAtuacao").html('');
        if (res && res.status && res.dados) {
        if (res.dados.length) {
            var especialidades = [];
            $("#areaAtuacao").append('<option value="">Todas</option>');
            res.dados.forEach(function(item) {
            $("#areaAtuacao").append('<option value="' + item.ID_AREA_ATUACAO + '">' + item.DS_AREA_ATUACAO +
                '</option>');
            })
        } else {
            $("#areaAtuacao").html('<option value="">Especialidade sem área de atuação</option>');

        }
        }
    });
    }

    function setupSituacao() {
    //  var select_tipo_situacao, $select_tipo_situacao;
    //  var select_situacao, $select_situacao;

    //  $select_tipo_situacao = $('select#tipoSituacao').selectize({
    //    onChange: function(value) {
    //      select_situacao.options = buscarDetalhesSituacao(value);
    //    }
    //  });

    //  $select_situacao = $('select#situacao').selectize();

    //  select_tipo_situacao = $select_tipo_situacao[0].selectize;
    //  select_situacao = $select_situacao[0].selectize;

    }

    $("#tipoSituacao").change(function(e) {
    var situacao = e.target.value
    var detalhes = {};
    if (situacao == 'A') {
        detalhes = {
        '': 'Todos os ativos',
        'E': 'Inoperante',
        'N': 'Interdição cautelar - parcial',
        'A': 'Regular',
        'X': 'Suspenso - parcial',
        'J': 'Suspenso por ordem judicial - parcial',
        'G': 'Sem o exercício da profissão na UF',
        }
    } else if (situacao == 'I') {
        detalhes = {
        '': 'Todos os inativos',
        'P': 'Aposentado',
        'L': 'Cancelado',
        'C': 'Cassado',
        'F': 'Falecido',
        'I': 'Interdição cautelar - total',
        'R': 'Suspensão temporária',
        'S': 'Suspenso - total',
        'O': 'Suspenso por ordem judicial - total',
        'T': 'Transferido',
        }
    } else {
        detalhes = {
        '': 'Selecione uma situação',
        }
    }

    var data = [];
    $("#situacao").html('');
    Object.keys(detalhes).forEach(function(key) {
        var title = detalhes[key];
        if (title) {
        //  data.push({
        //    text: title,
        //    value: key
        //  })
        $("#situacao").append('<option value="' + key + '">' + title + '</option>');
        }
    })
    //  return data;
    });

    function init() {

    //  $select_municipio = $('select#municipio').selectize();
    //  select_municipio = $select_municipio[0].selectize;

    listarUFs();
    listarEspecialidades();
    valuesEspecilidades('', true);

    //  restoreRota();

    //  $("#tipoSituacao").trigger("change");

    setTimeout(function() {
        //BRUNO restoreRota(true);
    }, 1000);
    }

    window.addEventListener("load", function() {
    init();
    })

    function restoreRota(autoSearch) {
    var urlParams = new URLSearchParams(window.location.search);
    var shouldSearch = false;

    var params = urlParams.values();

    function setValue(field) {
        var value = params[field];

        if(!value) return false;

        $("#" + field).val(value);
        $("[name=" + field + "]").val(value);

        return true;
    }

    var entries = urlParams.entries();
    var params = {};
    for (pair of entries) {
        params[pair[0]] = pair[1];
        if(pair[1]){
        shouldSearch = true;
        }
    }

    setValue('nome');

    setValue('crm');

    if(setValue('uf')){
        $("#uf").trigger("change");
        setTimeout(function(){
        setValue('municipio');
        },200);
    }

        if(setValue('tipoSituacao')){
        $("#tipoSituacao").trigger("change");
        }

        setValue('situacao');

        setValue('inscricao');

        if(setValue('especialidade')){
        $("#especialidade").trigger("change");

        setTimeout(function(){
        setValue('areaAtuacao');
        },200);

        }
    

    //  for(pair of entries) { 
    //    if(pair[1]){
    //      shouldSearch = true;
    //    }

    //    $("#" + pair[0]).val(pair[1]); 
    //    $("[name=" + pair[0] + "]").val(pair[1]); 

    //   //  if(pair[0] === "tipoSituacao"){
    //   //    console.log(pair[0]);
    //   //    $("#tipoSituacao").trigger("change");
    //   //  }

    //   //  if(pair[0] === "detalheSituacao"){
    //   //    setTimeout(function(){
    //   //      $("#" + pair[0]).val(pair[1]); 
    //   //      $("[name=" + pair[0] + "]").val(pair[1]); 
    //   //    },100);
    //   //  }
    //  }
    
    console.log(params);

    if (autoSearch && shouldSearch) {
    var page = params.pageNumber || 1; 
    getInfo(parseInt(page),true);
    setTimeout(function(){
        // $('#paginacao').pagination('go', params.pageNumber);
    },1000); 
    }
    }

    function newRota(params) {

    /*
    nomeMedico=&ufMedico=DF&crmMedico=&municipioMedico=1778&tipoInscricaoMedico=&situacaoMedico=&detalheSituacaoMedico=&especialidadeMedico=&areaAtuacaoMedico=&*/
    //${params[0].page}

    const page = params[0].page;
    const pageSize = params[0].pageSize;
    const medico = params[0].medico || {};

    /*
        medico: {
        nome: formData.nome,
        ufMedico: formData.uf,
        crmMedico: formData.crm,
        municipioMedico: formData.municipio,
        tipoInscricaoMedico: formData.inscricao,
        situacaoMedico: formData.tipoSituacao,
        detalheSituacaoMedico: formData.situacao,
        especialidadeMedico: formData.especialidade,
        areaAtuacaoMedico: formData.areaAtuacao
        },*/

    const search = `?nome=${medico.nome}&uf=${medico.ufMedico}&crm=${medico.crmMedico}&municipio=${medico.municipioMedico}&inscricao=${medico.tipoInscricaoMedico}&tipoSituacao=${medico.situacaoMedico}&situacao=${medico.detalheSituacaoMedico}&especialidade=${medico.especialidadeMedico}&areaAtuacao=${medico.areaAtuacaoMedico}&pageNumber=${page}&pageSize=${pageSize}`;

    window.history.pushState({}, "", `/busca-medicos/${search}`);
    }

    function renderPagination(pageNumber) {
    if(isNaN(pageNumber)){
    pageNumber = 1;
    }
    if(window.currentPage != ''){
    pageNumber = window.currentPage;
    }
    const qtdPaginas = [];
    for (let index = 0; index < resultado; index++) {
        qtdPaginas.push(index);
    }
    $('#paginacao').pagination({
        dataSource: qtdPaginas,
        pageSize: pageSize,
        pageNumber: pageNumber,
        showPrevious: false,
        showNext: false,
        callback: function(data, pagination) {
        if (initGet) {
            initGet = false;
            window.currentPage = pagination.pageNumber;
            getInfo(pagination.pageNumber, false);
        } else {
        if(recaptchaPublicKeyV2){
            grecaptcha.execute();
        }
        }
        }
    });
    }

})(jQuery);