$(document).ready(function () {
    const table = $('#jobapplications').DataTable({
        ajax: {
            url: '/api/v1/jobapplications/',
            dataSrc: 'job_applications'
        },
        serverSide: true,
        processing: true,
        stateSave: true,
        rowId: 'id',
        'columns': [
            {
                class: 'dt-control',
                orderable: false,
                data: null,
                defaultContent: '',
            },
            {
                data: 'id',
                name: 'id',
                visible: false,
                searchable: false,
            },
            {
                data: 'when',
                name: 'when',
                title: 'When',
                width: '100px',
            },
            {
                data: 'company',
                name: 'company',
                title: 'Company',
                width: '300px',
            },
            {
                data: 'title',
                name: 'title',
                title: 'Job Title',
                render: function(data, type, row, meta) {
                    if (type === 'display') {
                        return '<a href="' + row.posting + '" target="new">' + data + '</a>';
                    }
                    return data;
                }
            },
            {
                data: 'posting',
                name: 'posting',
                title: 'Job Posting',
                visible: false,
            },
            {
                data: 'confirm',
                name: 'confirm',
                title: 'Confirmation',
                visible: false,
            },
            {
                data: 'notes',
                name: 'notes',
                title: 'Notes',
                visible: false,
            },
            {
                data: 'active',
                name: 'active',
                title: 'Still active?',
                render: function(data, type, row) {
                    if (data === true) {
                        return 'Yes';
                    } else {
                        return 'No';
                    }
                },
                width: '100px',
            },
            {
                defaultContent: '<a href="#" onclick="var id=this.closest(\'tr\').id; window.location.href=\'/applications/\' + id + \'/edit\';"><button>Edit</button></a>',
                name: 'edit',
                title: 'Actions',
                width: '100px',
                placeholder: true,
            }
        ],
        'order': [
            [1, 'desc'],
            [2, 'asc'],
        ],
        layout: {
            top1End: function () {
                let toolbar = document.createElement('div');
                toolbar.innerHTML = '<a href="/applications/new-application/"><button id="add">Add</button></a>';

                return toolbar;
            },
            topStart: 'pageLength',
            topEnd: 'search',
            bottomStart: 'info',
            bottomEnd: 'paging',
        }
    });


    const applicationDetailRows = [];

    function applicationDetailFormat(d) {
        let retval = 'Company: ' + d.company + '<br>' +
            'Job Title: ' + d.title + '<br>';

        if (d.posting != '') {
            retval += 'Job posting: <a href="' + d.posting + '" target="_blank">' + d.posting + '</a><br>';
        }

        if (d.confirm != '') {
            retval += 'Confirmation: <a href="' + d.confirm + '" target="_blank">' + d.confirm + '</a><br>';
        }

        if (d.notes != '') {
            retval += 'Notes: ' + d.notes + '<br>';
        }

        return (retval);
    }

    table.on('click', 'tbody td.dt-control', function () {
        let tr = event.target.closest('tr');
        let row = table.row(tr);
        let idx = applicationDetailRows.indexOf(tr.id)

        if (row.child.isShown()) {
            tr.classList.remove('details');
            row.child.hide();

            // Remove from the 'open' array
            applicationDetailRows.splice(idx, 1);
        } else {
            tr.classList.add('details');
            row.child(applicationDetailFormat(row.data())).show();

            // Add to the 'open' array
            if (idx === -1) {
                applicationDetailRows.push(tr.id);
            }
        }
    });

    table.on('draw', () => {
        applicationDetailRows.forEach((id, i) => {
            let el = document.querySelector('#' + id + ' td.dt-control');

            if (el) {
                el.dispatchEvent(new Event('click', {bubbles: true}));
            }
        });
    });
});
