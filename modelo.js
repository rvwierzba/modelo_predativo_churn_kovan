/**
 * KovanModelo — Motor de Machine Learning Client-Side (Regressão Logística 5-Fold CV)
 * MBA Executivo em IA e Dados para Negócios · Inteli x Lenovo
 */
var KovanModelo = (function () {
  "use strict";

  var COLUNAS = [
    "meses_desde_ultima_compra",
    "meses_com_compra_12m",
    "queda_receita_trimestral",
    "qtd_pedidos_12m",
    "receita_12m",
    "ticket_medio"
  ];

  function sigmoid(z) {
    if (z > 20) return 1;
    if (z < -20) return 0;
    return 1 / (1 + Math.exp(-z));
  }

  function calcularAUC(labels, scores) {
    var pairs = [];
    var nPos = 0, nNeg = 0;
    for (var i = 0; i < labels.length; i++) {
      var y = labels[i] ? 1 : 0;
      if (y === 1) nPos++; else nNeg++;
      pairs.push({ y: y, s: scores[i] });
    }
    if (nPos === 0 || nNeg === 0) return 0.5;
    pairs.sort(function (a, b) { return a.s - b.s; });

    var rankSum = 0;
    var i = 0;
    while (i < pairs.length) {
      var j = i;
      while (j < pairs.length && pairs[j].s === pairs[i].s) j++;
      var avgRank = (i + 1 + j) / 2;
      for (var k = i; k < j; k++) {
        if (pairs[k].y === 1) rankSum += avgRank;
      }
      i = j;
    }
    var u = rankSum - (nPos * (nPos + 1)) / 2;
    return Math.max(0.5, Math.min(1.0, u / (nPos * nNeg)));
  }

  function treinarRegressaoLogistica(X, y, l2) {
    l2 = l2 || 0.01;
    var n = X.length;
    var d = X[0].length;
    var w = new Array(d).fill(0);
    var b = 0;
    var lr = 0.05;
    var epochs = 120;

    for (var epoch = 0; epoch < epochs; epoch++) {
      var gradW = new Array(d).fill(0);
      var gradB = 0;
      for (var i = 0; i < n; i++) {
        var dot = b;
        for (var j = 0; j < d; j++) dot += w[j] * X[i][j];
        var p = sigmoid(dot);
        var err = p - y[i];
        for (var j = 0; j < d; j++) gradW[j] += err * X[i][j];
        gradB += err;
      }
      for (var j = 0; j < d; j++) {
        w[j] -= lr * (gradW[j] / n + l2 * w[j]);
      }
      b -= lr * (gradB / n);
    }
    return { w: w, b: b };
  }

  function rodar(linhas, capacidade) {
    capacidade = capacidade || 138;
    if (!linhas || !linhas.length) {
      throw new Error("Planilha vazia ou sem linhas válidas.");
    }

    // 1. Agrupar por account_id
    var contasMap = {};
    for (var i = 0; i < linhas.length; i++) {
      var l = linhas[i];
      var id = String(l.account_id || "").trim();
      if (!id) continue;
      if (!contasMap[id]) {
        contasMap[id] = {
          account_id: id,
          segment: l.segment || "Enterprise",
          country: l.country || "LATAM",
          periodos: []
        };
      }
      contasMap[id].periodos.push({
        periodo: String(l.periodo || ""),
        churn_label: Number(l.churn_label) === 1 ? 1 : 0,
        receita: Number(l.receita_usd) || 0,
        pedidos: Number(l.qtd_pedidos) || 0
      });
    }

    // 2. Extrair features por conta
    var contas = [];
    var keys = Object.keys(contasMap);
    for (var k = 0; k < keys.length; k++) {
      var c = contasMap[keys[k]];
      c.periodos.sort(function (a, b) { return a.periodo.localeCompare(b.periodo); });

      var ultimos12 = c.periodos.slice(-12);
      var rec12 = 0;
      var ped12 = 0;
      var mesesComCompra = 0;
      var mesesSemCompra = 0;
      var recUltimoTrimestre = 0;
      var recPenultimoTrimestre = 0;

      for (var p = 0; p < ultimos12.length; p++) {
        var it = ultimos12[p];
        rec12 += it.receita;
        ped12 += it.pedidos;
        if (it.receita > 0 || it.pedidos > 0) {
          mesesComCompra++;
        }
      }

      // Meses desde a última compra
      for (var p = c.periodos.length - 1; p >= 0; p--) {
        if (c.periodos[p].receita > 0 || c.periodos[p].pedidos > 0) break;
        mesesSemCompra++;
      }

      var nPer = c.periodos.length;
      if (nPer >= 3) {
        recUltimoTrimestre = c.periodos.slice(-3).reduce(function (s, x) { return s + x.receita; }, 0);
      }
      if (nPer >= 6) {
        recPenultimoTrimestre = c.periodos.slice(-6, -3).reduce(function (s, x) { return s + x.receita; }, 0);
      }

      var quedaReceita = 0;
      if (recPenultimoTrimestre > 0) {
        quedaReceita = (recPenultimoTrimestre - recUltimoTrimestre) / recPenultimoTrimestre;
      }

      var ticketMedio = ped12 > 0 ? rec12 / ped12 : 0;
      var churnFinal = c.periodos[c.periodos.length - 1].churn_label;

      contas.push({
        account_id: c.account_id,
        segment: c.segment,
        country: c.country,
        churn: churnFinal === 1,
        valor_em_risco: rec12,
        meses_desde_ultima_compra: mesesSemCompra,
        meses_com_compra_12m: mesesComCompra,
        features: [
          mesesSemCompra,
          mesesComCompra,
          Math.max(-1, Math.min(2, quedaReceita)),
          ped12,
          Math.log1p(rec12),
          Math.log1p(ticketMedio)
        ]
      });
    }

    if (contas.length < 10) {
      throw new Error("Poucas contas para treinamento. Verifique a planilha.");
    }

    // 3. Normalização z-score das features
    var nFeat = COLUNAS.length;
    var medias = new Array(nFeat).fill(0);
    var desvios = new Array(nFeat).fill(0);

    for (var i = 0; i < contas.length; i++) {
      for (var j = 0; j < nFeat; j++) {
        medias[j] += contas[i].features[j];
      }
    }
    for (var j = 0; j < nFeat; j++) medias[j] /= contas.length;

    for (var i = 0; i < contas.length; i++) {
      for (var j = 0; j < nFeat; j++) {
        var d = contas[i].features[j] - medias[j];
        desvios[j] += d * d;
      }
    }
    for (var j = 0; j < nFeat; j++) {
      desvios[j] = Math.sqrt(desvios[j] / contas.length) || 1;
    }

    var X = [];
    var y = [];
    for (var i = 0; i < contas.length; i++) {
      var xNorm = [];
      for (var j = 0; j < nFeat; j++) {
        xNorm.push((contas[i].features[j] - medias[j]) / desvios[j]);
      }
      X.push(xNorm);
      y.push(contas[i].churn ? 1 : 0);
    }

    // 4. 5-Fold Cross Validation
    var kFolds = 5;
    var oofScores = new Array(contas.length).fill(0);

    for (var f = 0; f < kFolds; f++) {
      var xTrain = [], yTrain = [], xValIdx = [];
      for (var i = 0; i < contas.length; i++) {
        if (i % kFolds === f) {
          xValIdx.push(i);
        } else {
          xTrain.push(X[i]);
          yTrain.push(y[i]);
        }
      }
      var modelFold = treinarRegressaoLogistica(xTrain, yTrain, 0.02);
      for (var v = 0; v < xValIdx.length; v++) {
        var idx = xValIdx[v];
        var dot = modelFold.b;
        for (var j = 0; j < nFeat; j++) dot += modelFold.w[j] * X[idx][j];
        oofScores[idx] = sigmoid(dot);
      }
    }

    var aucOOF = calcularAUC(y, oofScores);

    // 5. Treinar modelo final em 100% dos dados para pesos interpretáveis
    var modeloFinal = treinarRegressaoLogistica(X, y, 0.02);
    var pesos = {};
    for (var j = 0; j < nFeat; j++) {
      pesos[COLUNAS[j]] = modeloFinal.w[j];
    }

    // 6. Montar Fila de Priorização por Valor Esperado
    for (var i = 0; i < contas.length; i++) {
      contas[i].escore = oofScores[i];
      contas[i].valor_esperado = Math.round(contas[i].escore * contas[i].valor_em_risco);
    }

    contas.sort(function (a, b) {
      return (b.valor_esperado - a.valor_esperado) || (b.escore - a.escore);
    });

    var fila = contas.slice(0, capacidade);
    var acertos = 0;
    var valorEsperadoTotal = 0;

    for (var i = 0; i < fila.length; i++) {
      fila[i].posicao = i + 1;
      if (fila[i].churn) acertos++;
      valorEsperadoTotal += fila[i].valor_esperado;
    }

    return {
      contas: contas.length,
      auc: aucOOF,
      acertos_fila: acertos,
      valor_esperado_fila: valorEsperadoTotal,
      pesos: pesos,
      fila: fila,
      todasContas: contas
    };
  }

  function contexto(resultado) {
    if (!resultado) return null;
    return {
      auc: resultado.auc,
      contas_total: resultado.contas,
      acertos_fila: resultado.acertos_fila,
      valor_esperado_total: resultado.valor_esperado_fila,
      pesos: resultado.pesos,
      top_contas: resultado.fila.slice(0, 15).map(function (c) {
        return {
          account_id: c.account_id,
          segment: c.segment,
          country: c.country,
          escore: c.escore,
          receita_usd: c.valor_em_risco,
          valor_esperado: c.valor_esperado,
          churn: c.churn
        };
      })
    };
  }

  function guardar(ctx) {
    try {
      localStorage.setItem("kovan_modelo_ctx", JSON.stringify(ctx));
    } catch (e) {}
  }

  function recuperar() {
    try {
      var d = localStorage.getItem("kovan_modelo_ctx");
      return d ? JSON.parse(d) : null;
    } catch (e) {
      return null;
    }
  }

  return {
    COLUNAS: COLUNAS,
    rodar: rodar,
    contexto: contexto,
    guardar: guardar,
    recuperar: recuperar
  };
})();
