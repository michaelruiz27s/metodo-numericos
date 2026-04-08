function toggleSubmenu(id) {
  const submenu = document.getElementById(id);
  const isVisible = submenu.style.display === 'block';

  // No cerramos los demás, solo alternamos este
  submenu.style.display = isVisible ? 'none' : 'block';
}

//Metodo de biseccion//
function cargarResultados() {
  fetch("http://127.0.0.1:5000/resultados-biseccion")
    .then(response => response.json())
    .then(data => {
      const tbody = document.querySelector("#tabla-resultados tbody");
      tbody.innerHTML = "";
      data.forEach(fila => {
        const tr = document.createElement("tr");
        fila.forEach(celda => {
          const td = document.createElement("td");
          td.textContent = celda;
          tr.appendChild(td);
        });
        tbody.appendChild(tr);
      });
    })
    .catch(error => {
      console.error("Error cargando los datos:", error);
    });
    actualizarSelect();

}
function buscarPorEjercicio(event) {
  event.preventDefault(); 

  const ejercicio = document.getElementById("ejercicio").value;

  if (!ejercicio) {
      alert("Por favor ingrese un número de ejercicio.");
      return;
  }

  fetch(`/buscar_ejercicio/${ejercicio}`)
      .then(response => response.json())
      .then(data => {
          const tbody = document.querySelector("#tabla-resultados tbody");
          tbody.innerHTML = ""; 

          if (data.length === 0) {
              tbody.innerHTML = "<tr><td colspan='9' style='text-align:center;'>No se encontraron resultados</td></tr>";
              return;
          }

          data.forEach(row => {
              const tr = document.createElement("tr");

              tr.innerHTML = `
                  <td>${row.ejercicio}</td>
                  <td>${row.iteracion}</td>
                  <td>${row.xa}</td>
                  <td>${row.xb}</td>
                  <td>${row.fx_xa}</td>
                  <td>${row.fx_xb}</td>
                  <td>${row.xr}</td>
                  <td>${row.fx_xr}</td>
                  <td>${row.ea}</td>
              `;

              tbody.appendChild(tr);
          });
      })
      .catch(error => {
          console.error("Error al buscar el ejercicio:", error);
      });
}

// ✅ Se ejecuta todo cuando carga la página
document.addEventListener("DOMContentLoaded", function () {
  cargarResultados();

  const form = document.querySelector("form");
  form.addEventListener("submit", function (event) {
    event.preventDefault();

    const formData = new FormData(form);
    fetch("http://127.0.0.1:5000/biseccion", {
      method: "POST",
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      console.log("Servidor:", data.mensaje);
      cargarResultados();
      actualizarSelect();

      const img = document.getElementById("grafica-biseccion");
      img.src = data.imagen + "?" + new Date().getTime(); 
      img.style.display = "block";s
    })
    
      .catch(error => {
        console.error("Error al enviar los datos:", error);
      });

  });
});


function eliminarEjercicio() {
  const ejercicio = document.getElementById("ejercicio").value;

  if (!ejercicio) {
    alert("Por favor, ingresa el número de ejercicio a eliminar.");
    return;
  }

  if (!confirm(`¿Estás seguro de eliminar los datos del ejercicio #${ejercicio}?`)) {
    return;
  }

  fetch(`http://127.0.0.1:5000/eliminar-biseccion/${ejercicio}`, {
    method: "DELETE"
  })
    .then(response => response.text())
    .then(msg => {
      alert(msg);
      cargarResultados(); 
      actualizarSelect();
    })
    .catch(error => {
      console.error("Error al eliminar:", error);
      alert("Error al eliminar los datos.");
    });
}

function actualizarEjercicio() {
  const form = document.querySelector("form");
  const formData = new FormData(form);

  fetch("http://127.0.0.1:5000/actualizar-biseccion", {
    method: "POST",
    body: formData
  })
    .then(response => response.text())
    .then(data => {
      console.log("✅ Actualización completada");
      cargarResultados(); 
      actualizarSelect();

    })
    .catch(error => {
      console.error("❌ Error al actualizar:", error);
    });
}


function actualizarSelect() {
  fetch('/resultados-biseccion')
    .then(res => res.json())
    .then(data => {
      const ejerciciosUnicos = [...new Set(data.map(row => row[0]))]; 
      const select = document.getElementById('ejercicioSelect');
      select.innerHTML = '';

      ejerciciosUnicos.forEach(ej => {
        const option = document.createElement('option');
        option.value = ej;
        option.textContent = `Ejercicio ${ej}`;
        select.appendChild(option);
      });

      if (ejerciciosUnicos.length > 0) {
        select.value = ejerciciosUnicos[ejerciciosUnicos.length - 1]; 
        cargarGrafica();
        
      }
    });
}



// Metodo de FALSA POSICION

function cargarResultadosFalsa() {
  fetch('http://127.0.0.1:5000/resultados-falsa-posicion')
    .then(response => response.json())
    .then(data => {
      const tabla = document.getElementById('tabla-resultados-falsa').getElementsByTagName('tbody')[0];
      tabla.innerHTML = '';

      data.forEach(fila => {
        const nuevaFila = tabla.insertRow();
        fila.forEach(valor => {
          const celda = nuevaFila.insertCell();
          celda.textContent = valor;
        });
      });
    })
    .catch(error => console.error('Error cargando resultados:', error));
    actualizarSelectFalsa();   
  }
function eliminarEjercicioFalsa(event) {
  event.preventDefault();
  const ejercicio = document.getElementById('ejercicio-falsa').value;

  if (!ejercicio) {
    alert('Por favor, ingresa el número de ejercicio a eliminar.');
    return;
  }

  fetch(`http://127.0.0.1:5000/eliminar-falsa-posicion/${ejercicio}`, {
    method: 'DELETE'
  })
    .then(response => response.text())
    .then(data => {
      alert(data);
      cargarResultadosFalsa();
      actualizarSelectFalsa();     
    })
    .catch(error => console.error('Error al eliminar ejercicio:', error));
}

function actualizarEjercicioFalsa(event) {
  event.preventDefault();
  const formData = new FormData();
  formData.append('ejercicio', document.getElementById('ejercicio-falsa').value);
  formData.append('funcion', document.getElementById('funcion-falsa').value);
  formData.append('xa', document.getElementById('xa-falsa').value);
  formData.append('xb', document.getElementById('xb-falsa').value);
  formData.append('es', document.getElementById('es-falsa').value);

  fetch('http://127.0.0.1:5000/actualizar-falsa-posicion', {
    method: 'POST',
    body: formData
  })
    .then(response => response.text())
    .then(data => {
      alert(data);
      cargarResultadosFalsa();
      actualizarSelectFalsa();     
    })
    .catch(error => console.error('Error al actualizar ejercicio:', error));
}
function buscarPorEjercicioFalsa(event) {
  event.preventDefault();
  const ejercicio = document.getElementById("ejercicio-falsa").value;

  if (!ejercicio) {
    alert("Por favor, ingrese un número de ejercicio.");
    return;
  }

  fetch(`/buscar_ejercicio_falsa/${ejercicio}`)
    .then(response => response.json())
    .then(data => {
      const tbody = document.querySelector("#tabla-resultados-falsa tbody");
      tbody.innerHTML = "";

      if (data.length === 0) {
        tbody.innerHTML = "<tr><td colspan='9' style='text-align:center;'>No se encontraron resultados</td></tr>";
        return;
      }

      data.forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${row.ejercicio}</td>
          <td>${row.iteracion}</td>
          <td>${row.xa}</td>
          <td>${row.xb}</td>
          <td>${row.fxa}</td>
          <td>${row.fxb}</td>
          <td>${row.xr}</td>
          <td>${row.fxr}</td>
          <td>${row.ea}</td>
        `;
        tbody.appendChild(tr);
      });
    });
}

function actualizarSelectFalsa() {
  fetch('/resultados-falsa-posicion')
    .then(res => res.json())
    .then(data => {
      const ejerciciosUnicos = [...new Set(data.map(row => row[0]))]; 
      const select = document.getElementById('ejercicioSelectFalsa');
      select.innerHTML = '';

      ejerciciosUnicos.forEach(ej => {
        const option = document.createElement('option');
        option.value = ej;
        option.textContent = `Ejercicio ${ej}`;
        select.appendChild(option);
      });

      if (ejerciciosUnicos.length > 0) {
        select.value = ejerciciosUnicos[ejerciciosUnicos.length - 1];
        cargarGraficaFalsa();
        
      }
    });
}
const formFalsa = document.querySelector('form[action="http://127.0.0.1:5000/falsa-posicion"]');
formFalsa.addEventListener("submit", function (event) {
  event.preventDefault();

  const formData = new FormData(formFalsa);
  fetch("http://127.0.0.1:5000/falsa-posicion", {
    method: "POST",
    body: formData
  })
    .then(response => response.text())
    .then(msg => {
      console.log("Servidor (Falsa):", msg);
      cargarResultadosFalsa(); 
      actualizarSelectFalsa();    
    })
    .catch(error => {
      console.error("Error Falsa Posición:", error);
    });
});








// Metodo de PUNTO FIJO

function cargarResultadosPuntoFijo() {
  fetch('http://127.0.0.1:5000/resultados-punto-fijo')
    .then(response => response.json())
    .then(data => {
      const tabla = document.getElementById('tabla-resultados-puntofijo').getElementsByTagName('tbody')[0];
      tabla.innerHTML = '';

      data.forEach(fila => {
        const nuevaFila = tabla.insertRow();
        fila.forEach(valor => {
          const celda = nuevaFila.insertCell();
          celda.textContent = valor;
        });
      });
    })
    .catch(error => console.error('Error cargando resultados Punto Fijo:', error));
    actualizarSelectPuntoFijo(); // después de cargarResultadosPuntoFijo()
}

function eliminarEjercicioPuntoFijo(event) {
  event.preventDefault();
  const ejercicio = document.getElementById('ejercicio-puntofijo').value;

  if (!ejercicio) {
    alert('Por favor, ingresa el número de ejercicio a eliminar.');
    return;
  }

  fetch(`http://127.0.0.1:5000/eliminar-punto-fijo/${ejercicio}`, {
    method: 'DELETE'
  })
    .then(response => response.text())
    .then(data => {
      alert(data);
      cargarResultadosPuntoFijo();
      actualizarSelectPuntoFijo(); // después de cargarResultadosPuntoFijo()
    })
    .catch(error => console.error('Error al eliminar ejercicio Punto Fijo:', error));
}

function actualizarEjercicioPuntoFijo(event) {
  event.preventDefault();
  const formData = new FormData();
  formData.append('ejercicio', document.getElementById('ejercicio-puntofijo').value);
  formData.append('funcion', document.getElementById('funcion-puntofijo').value);
  formData.append('x0', document.getElementById('x0-puntofijo').value);
  formData.append('es', document.getElementById('es-puntofijo').value);

  fetch('http://127.0.0.1:5000/actualizar-punto-fijo', {
    method: 'POST',
    body: formData
  })
    .then(response => response.text())
    .then(data => {
      alert(data);
      cargarResultadosPuntoFijo();
      actualizarSelectPuntoFijo(); // después de cargarResultadosPuntoFijo()
    })
    .catch(error => console.error('Error al actualizar ejercicio Punto Fijo:', error));
}
const formPuntoFijo = document.querySelector('form[action="http://127.0.0.1:5000/punto-fijo"]');
formPuntoFijo.addEventListener("submit", function (event) {
  event.preventDefault();

  const formData = new FormData(formPuntoFijo);
  fetch("http://127.0.0.1:5000/punto-fijo", {
    method: "POST",
    body: formData
  })
    .then(response => response.text())
    .then(msg => {
      console.log("Servidor (Punto Fijo):", msg);
      cargarResultadosPuntoFijo(); // 👈 actualizar tabla
      actualizarSelectPuntoFijo(); // ⬅️ actualiza combo y gráfica
    })
    .catch(error => {
      console.error("Error Punto Fijo:", error);
    });
});

function actualizarSelectPuntoFijo() {
  fetch('/resultados-punto-fijo')
    .then(res => res.json())
    .then(data => {
      const ejerciciosUnicos = [...new Set(data.map(row => row[0]))];
      const select = document.getElementById('ejercicioSelectPuntoFijo');
      select.innerHTML = '';

      ejerciciosUnicos.forEach(ej => {
        const option = document.createElement('option');
        option.value = ej;
        option.textContent = `Ejercicio ${ej}`;
        select.appendChild(option);
      });

      if (ejerciciosUnicos.length > 0) {
        select.value = ejerciciosUnicos[ejerciciosUnicos.length - 1]; // Último
        cargarGraficaPuntoFijo();
      }
    });
}
function cargarGraficaPuntoFijo() {
  const ejercicio = document.getElementById('ejercicioSelectPuntoFijo').value;
  document.getElementById('grafica-interactiva-puntofijo').src = `/static/imagenes/punto_fijo_${ejercicio}.html?t=${Date.now()}`;
}
function buscarPorEjercicioPuntoFijo(event) {
  event.preventDefault();
  const ejercicio = document.getElementById("ejercicio-puntofijo").value;

  if (!ejercicio) {
    alert("Por favor, ingrese un número de ejercicio.");
    return;
  }

  fetch(`/buscar_ejercicio_puntofijo/${ejercicio}`)
    .then(response => response.json())
    .then(data => {
      const tbody = document.querySelector("#tabla-resultados-puntofijo tbody");
      tbody.innerHTML = "";

      if (data.length === 0) {
        tbody.innerHTML = "<tr><td colspan='5' style='text-align:center;'>No se encontraron resultados</td></tr>";
        return;
      }

      data.forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${row.ejercicio}</td>
          <td>${row.iteracion}</td>
          <td>${row.xi}</td>
          <td>${row.gxi}</td>
          <td>${row.ea}</td>
        `;
        tbody.appendChild(tr);
      });
    })
    .catch(error => {
      console.error("Error al buscar ejercicio Punto Fijo:", error);
    });
}








// FUNCIONES PARA NEWTON-RAPHSON

function cargarResultadosNewton() {
  fetch('http://127.0.0.1:5000/resultados-newton-raphson')
    .then(response => response.json())
    .then(data => {
      const tabla = document.getElementById('tabla-resultados-newton').getElementsByTagName('tbody')[0];
      tabla.innerHTML = '';

      data.forEach(fila => {
        const nuevaFila = tabla.insertRow();
        fila.forEach(valor => {
          const celda = nuevaFila.insertCell();
          celda.textContent = valor;
        });
      });
    })
    .catch(error => console.error('Error cargando resultados Newton-Raphson:', error));
}

function eliminarEjercicioNewton(event) {
  event.preventDefault();
  const ejercicio = document.getElementById('ejercicio-newton').value;

  if (!ejercicio) {
    alert('Por favor, ingresa el número de ejercicio a eliminar.');
    return;
  }

  fetch(`http://127.0.0.1:5000/eliminar-newton-raphson/${ejercicio}`, {
    method: 'DELETE'
  })
    .then(response => response.text())
    .then(data => {
      alert(data);
      cargarResultadosNewton();
    })
    .catch(error => console.error('Error al eliminar ejercicio Newton-Raphson:', error));
}

function actualizarEjercicioNewton(event) {
  event.preventDefault();
  const formData = new FormData();
  formData.append('ejercicio', document.getElementById('ejercicio-newton').value);
  formData.append('funcion', document.getElementById('funcion-newton').value);
  formData.append('derivada', document.getElementById('derivada-newton').value);
  formData.append('x0', document.getElementById('x0-newton').value);
  formData.append('es', document.getElementById('es-newton').value);

  fetch('http://127.0.0.1:5000/actualizar-newton-raphson', {
    method: 'POST',
    body: formData
  })
    .then(response => response.text())
    .then(data => {
      alert(data);
      cargarResultadosNewton();
    })
    .catch(error => console.error('Error al actualizar ejercicio Newton-Raphson:', error));
}

// 🔥 FORMULARIO NEWTON-RAPHSON
const formNewton = document.querySelector('form[action="http://127.0.0.1:5000/newton-raphson"]');
formNewton.addEventListener("submit", function (event) {
  event.preventDefault();

  const formData = new FormData(formNewton);
  fetch("http://127.0.0.1:5000/newton-raphson", {
    method: "POST",
    body: formData
  })
    .then(response => response.text())
    .then(msg => {
      console.log("Servidor (Newton-Raphson):", msg);
      cargarResultadosNewton(); // 👈 actualizar tabla
    })
    .catch(error => {
      console.error("Error Newton-Raphson:", error);
    });
});




// FUNCIONES PARA SECANTE

function cargarResultadosSecante() {
  fetch('http://127.0.0.1:5000/resultados-secante')
    .then(response => response.json())
    .then(data => {
      const tabla = document.getElementById('tabla-resultados-secante').getElementsByTagName('tbody')[0];
      tabla.innerHTML = '';

      data.forEach(fila => {
        const nuevaFila = tabla.insertRow();
        fila.forEach(valor => {
          const celda = nuevaFila.insertCell();
          celda.textContent = valor;
        });
      });
    })
    .catch(error => console.error('Error cargando resultados Secante:', error));
    actualizarSelectSecante();
}

function eliminarEjercicioSecante(event) {
  event.preventDefault();
  const ejercicio = document.getElementById('ejercicio-secante').value;

  if (!ejercicio) {
    alert('Por favor, ingresa el número de ejercicio a eliminar.');
    return;
  }

  fetch(`http://127.0.0.1:5000/eliminar-secante/${ejercicio}`, {
    method: 'DELETE'
  })
    .then(response => response.text())
    .then(data => {
      alert(data);
      cargarResultadosSecante();
      actualizarSelectSecante();
    })
    .catch(error => console.error('Error al eliminar ejercicio Secante:', error));
}

function actualizarEjercicioSecante(event) {
  event.preventDefault();
  const formData = new FormData();
  formData.append('ejercicio', document.getElementById('ejercicio-secante').value);
  formData.append('funcion', document.getElementById('funcion-secante').value);
  formData.append('x0', document.getElementById('x0-secante').value);
  formData.append('x1', document.getElementById('x1-secante').value);
  formData.append('es', document.getElementById('es-secante').value);

  fetch('http://127.0.0.1:5000/actualizar-secante', {
    method: 'POST',
    body: formData
  })
    .then(response => response.text())
    .then(data => {
      alert(data);
      cargarResultadosSecante();
      actualizarSelectSecante();
    })
    .catch(error => console.error('Error al actualizar ejercicio Secante:', error));
}

const formSecante = document.querySelector('form[action="http://127.0.0.1:5000/secante"]');
formSecante.addEventListener("submit", function (event) {
  event.preventDefault();

  const formData = new FormData(formSecante);
  fetch("http://127.0.0.1:5000/secante", {
    method: "POST",
    body: formData
  })
    .then(response => response.text())
    .then(msg => {
      console.log("Servidor (Secante):", msg);
      cargarResultadosSecante(); // 👈 actualizar tabla
      actualizarSelectSecante();
    })
    .catch(error => {
      console.error("Error Secante:", error);
    });
});
function actualizarSelectSecante() {
  fetch('/resultados-secante')
    .then(res => res.json())
    .then(data => {
      const ejerciciosUnicos = [...new Set(data.map(row => row[0]))];
      const select = document.getElementById('ejercicioSelectSecante');
      select.innerHTML = '';

      ejerciciosUnicos.forEach(ej => {
        const option = document.createElement('option');
        option.value = ej;
        option.textContent = `Ejercicio ${ej}`;
        select.appendChild(option);
      });

      if (ejerciciosUnicos.length > 0) {
        select.value = ejerciciosUnicos[ejerciciosUnicos.length - 1];
        cargarGraficaSecante();
      }
    });
}

function cargarGraficaSecante() {
  const ejercicio = document.getElementById('ejercicioSelectSecante').value;
  document.getElementById('grafica-interactiva-secante').src = `/static/imagenes/secante_${ejercicio}.html?t=${Date.now()}`;
}

function buscarPorEjercicioSecante(event) {
  event.preventDefault();
  const ejercicio = document.getElementById("ejercicio-secante").value;

  if (!ejercicio) {
    alert("Por favor, ingrese un número de ejercicio.");
    return;
  }

  fetch(`/buscar_ejercicio_secante/${ejercicio}`)
    .then(response => response.json())
    .then(data => {
      const tbody = document.querySelector("#tabla-resultados-secante tbody");
      tbody.innerHTML = "";

      if (data.length === 0) {
        tbody.innerHTML = "<tr><td colspan='8' style='text-align:center;'>No se encontraron resultados</td></tr>";
        return;
      }

      data.forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${row.ejercicio}</td>
          <td>${row.iteracion}</td>
          <td>${row.xi_1}</td>
          <td>${row.xi}</td>
          <td>${row.fxi_1}</td>
          <td>${row.fxi}</td>
          <td>${row.xi_t}</td>
          <td>${row.ea}</td>
        `;
        tbody.appendChild(tr);
      });
    })
    .catch(error => {
      console.error("Error al buscar ejercicio Secante:", error);
    });
}










//Exportacion a Excel//
function exportarTabla(idTabla, nombreArchivo, nombreHoja) {
  const tabla = document.getElementById(idTabla);
  const wb = XLSX.utils.table_to_book(tabla, { sheet: nombreHoja });
  XLSX.writeFile(wb, nombreArchivo);
}


//Exportar todo a excel//
function exportarTodo() {
  // Crear un nuevo libro de Excel
  const wb = XLSX.utils.book_new();

  // Lista de tablas y nombres de hojas
  const tablas = [
    { id: 'tabla-resultados', nombre: 'Biseccion' },
    { id: 'tabla-resultados-falsa', nombre: 'FalsaPosicion' },
    { id: 'tabla-resultados-puntofijo', nombre: 'PuntoFijo' },
    { id: 'tabla-resultados-newton', nombre: 'NewtonRaphson' },
    { id: 'tabla-resultados-secante', nombre: 'Secante' },
    { id: 'tabla-resultados-newton-sistemas', nombre: 'NR SENL' }

  ];

  // Recorrer cada tabla y agregarla como hoja
  tablas.forEach(tablaInfo => {
    const tabla = document.getElementById(tablaInfo.id);
    if (tabla) {
      const ws = XLSX.utils.table_to_sheet(tabla);
      XLSX.utils.book_append_sheet(wb, ws, tablaInfo.nombre);
    }
  });

  // Guardar el archivo
  XLSX.writeFile(wb, 'metodos_numericos_completo.xlsx');
}
function cargarResultadosNewtonSistemas() {
  fetch('http://127.0.0.1:5000/resultados-newton-sistemas')
    .then(response => response.json())
    .then(data => {
      const tabla = document.getElementById('tabla-resultados-newton-sistemas').getElementsByTagName('tbody')[0];
      tabla.innerHTML = '';

      data.forEach(fila => {
        const nuevaFila = tabla.insertRow();

        // Ejercicio
        const celdaEjercicio = nuevaFila.insertCell();
        celdaEjercicio.textContent = fila[0];

        // Iteración
        const celdaIteracion = nuevaFila.insertCell();
        celdaIteracion.textContent = fila[1];

        // X
        // Y
        const celdaX = nuevaFila.insertCell();
        celdaX.innerHTML = `
          ${parseFloat(fila[2]).toFixed(8)}<br>
          ${parseFloat(fila[3]).toFixed(8)}
        `;
        

        // F(x,y)
        const celdaFx = nuevaFila.insertCell();
        celdaFx.innerHTML = `
          ${parseFloat(fila[4]).toFixed(8)}<br>
          ${parseFloat(fila[5]).toFixed(8)}
        `;
        

        // Jacobiano (J11, J12, J21, J22)
        const celdaJ = nuevaFila.insertCell();
        celdaJ.innerHTML = `
          ${parseFloat(fila[6]).toFixed(8)} ${parseFloat(fila[7]).toFixed(8)}<br>
          ${parseFloat(fila[8]).toFixed(8)} ${parseFloat(fila[9]).toFixed(8)}
        `;
        


        // Inversa del Jacobiano (invJ11, invJ12, invJ21, invJ22)
        const celdaInvJ = nuevaFila.insertCell();
        celdaInvJ.innerHTML = `
          ${parseFloat(fila[10]).toFixed(8)} ${parseFloat(fila[11]).toFixed(8)}<br>
          ${parseFloat(fila[12]).toFixed(8)} ${parseFloat(fila[13]).toFixed(8)}
        `;
        

        // x y y nuevas
        const celdaDelta = nuevaFila.insertCell();
        celdaDelta.innerHTML = `
          ${parseFloat(fila[14]).toFixed(8)}<br>
          ${parseFloat(fila[15]).toFixed(8)}
        `;
        
        // e1 y e2
        const celdaError = nuevaFila.insertCell();
        celdaError.innerHTML = `
          ${fila[16] !== 0 ? parseFloat(fila[16]).toFixed(8) : '-'}<br>
          ${fila[17] !== 0 ? parseFloat(fila[17]).toFixed(8) : '-'}
        `;
        
      });
    })
    .catch(error => console.error('Error cargando resultados Newton Sistemas:', error));
}


function eliminarEjercicioNewtonSistemas(event) {
  event.preventDefault();
  const ejercicio = document.getElementById('ejercicio-newton-sistemas').value;

  if (!ejercicio) {
    alert('Por favor, ingresa el número de ejercicio a eliminar.');
    return;
  }

  fetch(`http://127.0.0.1:5000/eliminar-newton-sistemas/${ejercicio}`, {
    method: 'DELETE'
  })
    .then(response => response.text())
    .then(data => {
      alert(data);
      cargarResultadosNewtonSistemas();
    })
    .catch(error => console.error('Error al eliminar ejercicio Newton Sistemas:', error));
}





/*Falta arreglar*/
function actualizarEjercicioNewtonSistemas(event) {
  event.preventDefault();

  // ✅ Seleccionamos el formulario correcto de Newton-Sistemas
  const form = document.querySelector('form[action="http://127.0.0.1:5000/newton-sistemas"]');
  
  // ✅ Creamos el FormData directamente desde el formulario
  const formData = new FormData(form);

  // ✅ Enviamos la solicitud POST a /actualizar-newton-sistemas
  fetch('http://127.0.0.1:5000/actualizar-newton-sistemas', {
    method: 'POST',
    body: formData
  })
    .then(response => response.text())
    .then(data => {
      alert(data);                // ✅ Mostramos el mensaje del servidor
      cargarResultadosNewtonSistemas(); // ✅ Recargamos la tabla de resultados
    })
    .catch(error => {
      console.error('Error al actualizar ejercicio Newton Sistemas:', error);
    });
}





// Cargar lista de ejercicios al iniciar
window.onload = () => {
  fetch('/resultados-biseccion')
      .then(res => res.json())
      .then(data => {
          const ejerciciosUnicos = [...new Set(data.map(row => row[0]))]; // row[0] = ejercicio
          const select = document.getElementById('ejercicioSelect');
          ejerciciosUnicos.forEach(ej => {
              const option = document.createElement('option');
              option.value = ej;
              option.textContent = `Ejercicio ${ej}`;
              select.appendChild(option);
          });

          if (ejerciciosUnicos.length > 0) {
              select.value = ejerciciosUnicos[0];
              cargarGrafica();
          }
      });
};

// Cargar la gráfica al cambiar de ejercicio
function cargarGrafica() {
  const ejercicio = document.getElementById('ejercicioSelect').value;
  document.getElementById('grafica-interactiva').src = `/static/imagenes/biseccion_${ejercicio}.html?t=${Date.now()}`;
}

window.addEventListener('load', () => {
  fetch('/resultados-falsa-posicion')
    .then(res => res.json())
    .then(data => {
      const ejerciciosUnicos = [...new Set(data.map(row => row[0]))]; // row[0] = ejercicio
      const select = document.getElementById('ejercicioSelectFalsa');
      ejerciciosUnicos.forEach(ej => {
        const option = document.createElement('option');
        option.value = ej;
        option.textContent = `Ejercicio ${ej}`;
        select.appendChild(option);
      });

      if (ejerciciosUnicos.length > 0) {
        select.value = ejerciciosUnicos[0];
        cargarGraficaFalsa();
      }
    });
});

function cargarGraficaFalsa() {
  const ejercicio = document.getElementById('ejercicioSelectFalsa').value;
  document.getElementById('grafica-interactiva-falsa').src = `/static/imagenes/falsa_posicion_${ejercicio}.html?t=${Date.now()}`;
}

// 🚀 Cargar resultados automáticamente al abrir la página
window.addEventListener('load', function () {
  cargarResultados();         // Bisección
  cargarResultadosFalsa();    // Falsa Posición
  cargarResultadosPuntoFijo(); // Punto Fijo
  cargarResultadosNewton();    // Newton-Raphson
  cargarResultadosSecante(); // ⬅️ Agregamos esta nueva carga automática
  cargarResultadosNewtonSistemas();  // 🚀 también cargarlo al abrir la página
});


