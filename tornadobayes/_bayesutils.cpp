#include <Python.h>

static PyObject *
utils_words_cnt_by_cat(PyObject *self, PyObject *args) {
    const char *command;
    int sts;

    if (!PyArg_ParseTuple(args, "s", &command)) {
        return NULL;
    }
    sts = system(command);
    return Py_BuildValue("i", sts);
}

static PyMethodDef BayesUtilsMethods[] = {
    {"words_cnt_by_cat", utils_words_cnt_by_cat, METH_VARARGS,
     "Calculate number of words in category"},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
init_bayesutils(void) {
    (void) Py_InitModule("_bayesutils", BayesUtilsMethods);
}
